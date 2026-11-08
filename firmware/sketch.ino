#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>

// ============================================================================
// HARDWARE PIN DEFINITIONS (Matching firmware/diagram.json)
// ============================================================================
#define TRIG_PIN       5
#define ECHO_PIN       18
#define SERVO_PIN      13
#define LED_RED_PIN    12
#define LED_GREEN_PIN  14
#define BUZZER_PIN     27
#define POT_PIN        34

// ============================================================================
// PHYSICAL DRAIN CONSTANTS
// ============================================================================
const float MOUNT_HEIGHT_CM = 200.0; // Sensor mount height from channel floor
const float MAX_DRAIN_DEPTH = 180.0; // Maximum channel overflow depth before flood

// ============================================================================
// NETWORK & MQTT CONFIGURATION
// ============================================================================
// Set to "broker.hivemq.com" (works seamlessly in Wokwi Web & VS Code with zero setup)
// or "10.0.2.2" (if running a local Mosquitto broker inside Docker / host machine)
#define USE_LOCAL_BROKER false

const char* ssid        = "Wokwi-GUEST";
const char* password    = "";
#if USE_LOCAL_BROKER
  const char* mqtt_server = "10.0.2.2";
#else
  const char* mqtt_server = "broker.hivemq.com";
#endif
const int   mqtt_port   = 1883;
const char* node_id     = "drain-01";

// ============================================================================
// GLOBAL OBJECTS & STATE
// ============================================================================
WiFiClient espClient;
PubSubClient client(espClient);
Servo gateServo;

float lastDistanceCm = -1.0;
int currentGateAngle = 0;
unsigned long lastPublishTime = 0;
const unsigned long PUBLISH_INTERVAL_MS = 5000;

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

    long duration = pulseIn(ECHO_PIN, HIGH, 30000);
    if (duration == 0) {
      samples[i] = MOUNT_HEIGHT_CM;
    } else {
      samples[i] = duration * 0.0343 / 2.0;
    }
    delay(10);
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
  StaticJsonDocument<256> doc;
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
      gateServo.write(currentGateAngle);
      Serial.printf("[SCADA COMMAND] Received Remote Gate Angle: %d deg (Topic: %s)\n", currentGateAngle, topic);
    }
  }
}

void reconnectMQTT() {
  if (!client.connected()) {
    Serial.printf("[MQTT] Connecting to %s:%d as %s... ", mqtt_server, mqtt_port, node_id);
    if (client.connect(node_id, "flood/v1/drain-01/status", 1, true, "offline")) {
      Serial.println("CONNECTED!");
      // Subscribe to both SCADA command topic conventions
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
  Serial.printf(F("   Node: %s | Servo: GPIO %d | Trig: GPIO %d | Echo: GPIO %d\n"), node_id, SERVO_PIN, TRIG_PIN, ECHO_PIN);
  Serial.println(F("=============================================="));

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(POT_PIN, INPUT);

  digitalWrite(LED_GREEN_PIN, HIGH);
  digitalWrite(LED_RED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  gateServo.setPeriodHertz(50);
  gateServo.attach(SERVO_PIN, 500, 2400);
  gateServo.write(0); // Default Open

  Serial.println(F("[SERVO] Gate attached to GPIO 13. Default angle: 0 deg (OPEN)."));

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);

  Serial.println(F("[SYSTEM] Ready! Listening to sensors and MQTT..."));
}

// ============================================================================
// MAIN LOOP
// ============================================================================
void loop() {
  if (WiFi.status() == WL_CONNECTED && !client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  float distCm = getMedianDistance();
  float waterDepthCm = constrain(MOUNT_HEIGHT_CM - distCm, 0.0, MAX_DRAIN_DEPTH);
  float fillPercentage = (waterDepthCm / MAX_DRAIN_DEPTH) * 100.0;
  float rainMmH = readRainRateMmH();

  // Local Edge Autonomy (Autonomous Safety Triggers)
  if (fillPercentage >= 70.0) {
    // High Water Level -> Close Gate & Alarm
    currentGateAngle = 90;
    digitalWrite(LED_RED_PIN, HIGH);
    digitalWrite(LED_GREEN_PIN, LOW);
    tone(BUZZER_PIN, 1000, 200);
  } else if (fillPercentage <= 50.0) {
    // Normal Water Level -> Open Gate
    currentGateAngle = 0;
    digitalWrite(LED_RED_PIN, LOW);
    digitalWrite(LED_GREEN_PIN, HIGH);
    noTone(BUZZER_PIN);
  }

  gateServo.write(currentGateAngle);

  // Trigger Instant Telemetry Update on Slider Shift (>= 5cm difference) or Timer Interval
  unsigned long now = millis();
  if (abs(distCm - lastDistanceCm) >= 5.0 || (now - lastPublishTime >= PUBLISH_INTERVAL_MS)) {
    lastDistanceCm = distCm;
    lastPublishTime = now;

    Serial.printf("[SENSOR] Dist: %.1f cm | Depth: %.1f cm (%.1f%%) -> Gate: %d deg | Rain: %.1f mm/h\n",
                  distCm, waterDepthCm, fillPercentage, currentGateAngle, rainMmH);

    if (client.connected()) {
      StaticJsonDocument<256> doc;
      doc["node"]           = node_id;
      doc["node_id"]        = node_id;
      doc["depth_cm"]       = waterDepthCm;
      doc["water_depth_cm"] = waterDepthCm;
      doc["fill_percentage"]= fillPercentage;
      doc["ratio"]          = fillPercentage / 100.0;
      doc["rain_mm_h"]      = rainMmH;
      doc["gate_deg"]       = currentGateAngle;
      doc["gate_angle"]     = currentGateAngle;
      doc["ts"]             = millis() / 1000;
      doc["rssi"]           = WiFi.RSSI();

      char buffer[256];
      serializeJson(doc, buffer);
      // Publish to both topic namespaces for complete backend compatibility
      client.publish("ews/telemetry/drain-01", buffer);
      client.publish("flood/v1/drain-01/telemetry", buffer);
    }
  }

  delay(100);
}
