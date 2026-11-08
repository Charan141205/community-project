#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ============================================================================
// HARDWARE PIN DEFINITIONS (Wokwi ESP32 Safe Pins)
// ============================================================================
#define TRIG_PIN       5
#define ECHO_PIN       18
#define SERVO_PIN      19
#define LED_RED_PIN    21
#define LED_GREEN_PIN  22
#define BUZZER_PIN     23
#define POT_PIN        34

// ============================================================================
// PHYSICAL DRAIN CONSTANTS
// ============================================================================
const float MOUNT_HEIGHT_CM = 200.0; // Sensor mount height from channel floor
const float MAX_DRAIN_DEPTH = 180.0; // Maximum channel overflow depth before flood

// ============================================================================
// DEPLOYMENT MODE & NETWORK CONFIGURATION
// ============================================================================
// Set to 1 when flashing physical hardware; 0 for Wokwi simulation
#define USE_PHYSICAL_HARDWARE 0

#if USE_PHYSICAL_HARDWARE
  const char* ssid        = "YOUR_WIFI_SSID";         // Physical Wi-Fi network SSID
  const char* password    = "YOUR_WIFI_PASSWORD";     // Physical Wi-Fi password
  const char* mqtt_server = "broker.hivemq.com";       // Production or local MQTT broker IP
#else
  const char* ssid        = "Wokwi-GUEST";            // Wokwi Virtual Wi-Fi
  const char* password    = "";                       // No password needed in Wokwi
  const char* mqtt_server = "broker.hivemq.com";       // Public cloud broker
#endif

const int   mqtt_port   = 1883;
const char* node_id     = "drain-01";

// ============================================================================
// GLOBAL OBJECTS & STATE
// ============================================================================
WiFiClient espClient;
PubSubClient client(espClient);

float lastDistanceCm = -1.0;
int currentGateAngle = 0;
unsigned long lastPublishTime = 0;
unsigned long lastMqttCheckTime = 0;
const unsigned long PUBLISH_INTERVAL_MS = 3000;

// ============================================================================
// NATIVE ESP32 SERVO PWM CONTROLLER (LEDC)
// Zero external library crashes, compatible with ESP32 Core 2.x and Core 3.x
// ============================================================================
void initServoPWM() {
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
  ledcAttach(SERVO_PIN, 50, 16);
#else
  ledcSetup(0, 50, 16);
  ledcAttachPin(SERVO_PIN, 0);
#endif
}

void setServoAngle(int angle) {
  angle = constrain(angle, 0, 180);
  // SG90 standard: 500 us (0 deg) to 2400 us (180 deg)
  // 50 Hz PWM period = 20,000 us, 16-bit resolution = 65,535 ticks
  long pulseWidthUs = 500 + ((long)angle * (2400 - 500) / 180);
  long duty = (pulseWidthUs * 65535L) / 20000L;
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
  ledcWrite(SERVO_PIN, duty);
#else
  ledcWrite(0, duty);
#endif
}

// ============================================================================
// 5-SAMPLE MEDIAN FILTER FOR ULTRASONIC SENSOR
// ============================================================================
float getMedianDistance() {
  float samples[5];
  for (int i = 0; i < 5; i++) {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH, 26000); // ~4.5m timeout
    if (duration == 0) {
      samples[i] = MOUNT_HEIGHT_CM;
    } else {
      samples[i] = (float)duration * 0.0343f / 2.0f;
    }
    delay(5);
  }

  // Insertion Sort
  for (int i = 0; i < 4; i++) {
    for (int j = i + 1; j < 5; j++) {
      if (samples[j] < samples[i]) {
        float temp = samples[i];
        samples[i] = samples[j];
        samples[j] = temp;
      }
    }
  }
  return samples[2]; // Median value
}

float readRainRateMmH() {
  int rawAdc = analogRead(POT_PIN);
  return (float)rawAdc / 4095.0f * 100.0f;
}

// ============================================================================
// MQTT CALLBACK (REMOTE SCADA COMMANDS)
// ============================================================================
void mqttCallback(char* topic, byte* payload, unsigned int length) {
#if ARDUINOJSON_VERSION_MAJOR >= 7
  JsonDocument doc;
#else
  StaticJsonDocument<256> doc;
#endif
  DeserializationError err = deserializeJson(doc, payload, length);
  if (!err) {
    int targetAngle = -1;
    if (doc.containsKey("gate_angle")) {
      targetAngle = doc["gate_angle"];
    } else if (doc.containsKey("gate_deg")) {
      targetAngle = doc["gate_deg"];
    }

    if (targetAngle >= 0) {
      targetAngle = constrain(targetAngle, 0, 90);
      currentGateAngle = targetAngle;
      setServoAngle(currentGateAngle);
      Serial.printf("[SCADA COMMAND] Remote Gate Angle: %d deg\n", currentGateAngle);
    }
  }
}

void reconnectMQTT() {
  if (!client.connected()) {
    Serial.printf("[MQTT] Connecting to %s... ", mqtt_server);
    if (client.connect(node_id, "flood/v1/drain-01/status", 1, true, "offline")) {
      Serial.println("CONNECTED!");
      client.subscribe("ews/cmd/drain-01");
      client.subscribe("flood/v1/drain-01/cmd");
      client.publish("flood/v1/drain-01/status", "online", true);
    } else {
      Serial.printf("FAILED (rc=%d)\n", client.state());
    }
  }
}

// ============================================================================
// SETUP & INITIALIZATION
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println(F("\n=============================================="));
  Serial.println(F("   flood-ews ESP32 Node Booting... "));
  Serial.println(F("=============================================="));

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(POT_PIN, INPUT);

  // Initialize LED states
  digitalWrite(LED_GREEN_PIN, HIGH);
  digitalWrite(LED_RED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  // Initialize Native LEDC Servo PWM
  initServoPWM();
  setServoAngle(0); // Default Open (0 deg)
  Serial.println(F("[HARDWARE] Native LEDC Servo initialized on GPIO 19. Initial angle: 0 deg (OPEN)."));

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);

  Serial.println(F("[SYSTEM] Ready! Listening to HC-SR04 ultrasonic sensor..."));
}

// ============================================================================
// MAIN LOOP (Non-blocking & responsive)
// ============================================================================
void loop() {
  unsigned long now = millis();

  // Non-blocking background MQTT reconnect every 5s if Wi-Fi connected
  if (now - lastMqttCheckTime >= 5000) {
    lastMqttCheckTime = now;
    if (WiFi.status() == WL_CONNECTED && !client.connected()) {
      reconnectMQTT();
    }
  }

  if (client.connected()) {
    client.loop();
  }

  // Read Sensors
  float distCm = getMedianDistance();
  float waterDepthCm = constrain(MOUNT_HEIGHT_CM - distCm, 0.0, MAX_DRAIN_DEPTH);
  float fillPercentage = (waterDepthCm / MAX_DRAIN_DEPTH) * 100.0f;
  float rainMmH = readRainRateMmH();

  // Instant Edge Autonomy (Safety Floodgate Closure)
  // When Distance <= 74cm (Water Depth >= 126cm / Fill >= 70%):
  // Close the floodgate immediately to prevent sewer backflow!
  if (fillPercentage >= 70.0f) {
    currentGateAngle = 90;
    digitalWrite(LED_RED_PIN, HIGH);
    digitalWrite(LED_GREEN_PIN, LOW);
    digitalWrite(BUZZER_PIN, HIGH); // Alarm siren
  } else if (fillPercentage <= 50.0f) {
    currentGateAngle = 0;
    digitalWrite(LED_RED_PIN, LOW);
    digitalWrite(LED_GREEN_PIN, HIGH);
    digitalWrite(BUZZER_PIN, LOW);
  }

  // Actuate Servo
  setServoAngle(currentGateAngle);

  // Publish Telemetry on Slider Shift (>= 5cm difference) or Timer Interval
  if (abs(distCm - lastDistanceCm) >= 5.0f || (now - lastPublishTime >= PUBLISH_INTERVAL_MS)) {
    lastDistanceCm = distCm;
    lastPublishTime = now;

    Serial.printf("[SENSOR] Distance: %.1f cm | Depth: %.1f cm (%.1f%%) -> Gate: %d deg\n",
                  distCm, waterDepthCm, fillPercentage, currentGateAngle);

    if (client.connected()) {
      char buffer[256];
      snprintf(buffer, sizeof(buffer),
        "{\"node\":\"%s\",\"node_id\":\"%s\",\"depth_cm\":%.1f,\"water_depth_cm\":%.1f,\"fill_percentage\":%.1f,\"ratio\":%.2f,\"rain_mm_h\":%.1f,\"gate_deg\":%d,\"gate_angle\":%d,\"ts\":%lu,\"rssi\":%d}",
        node_id, node_id, waterDepthCm, waterDepthCm, fillPercentage, fillPercentage / 100.0f, rainMmH, currentGateAngle, currentGateAngle, (unsigned long)(now / 1000), WiFi.RSSI()
      );
      client.publish("ews/telemetry/drain-01", buffer);
      client.publish("flood/v1/drain-01/telemetry", buffer);
    }
  }

  delay(50); // Fast 50ms cycle for instant UI slider responsiveness
}
