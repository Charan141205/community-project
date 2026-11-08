/**
 * flood-ews: Smart Community Flood & Urban Drainage Early Warning System
 * Node Firmware (ESP32 / Wokwi)
 *
 * SENSORS & ACTUATORS:
 * - HC-SR04 Ultrasonic Distance Sensor: Water level in drain channel
 * - Potentiometer (ADC GPIO34): Simulated Rain Gauge (0.0 to 100.0 mm/h)
 * - Micro Servo (GPIO19): Floodgate Actuator (0 deg = FULLY OPEN, 90 deg = FULLY CLOSED)
 * - Green LED (GPIO22): System/Connectivity Status (MQTT Online)
 * - Red LED (GPIO21): Warning/Critical Flood Indicator
 * - Buzzer (GPIO23): Local Autonomous Emergency Siren
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>

// ============================================================================
// NODE PRESET SELECTION (Change SELECTED_NODE to 1, 2, or 3 to test different nodes)
// ============================================================================
#define SELECTED_NODE 1

#if SELECTED_NODE == 1
  const char* NODE_ID = "drain-01";
  const char* LOCATION_NAME = "Moosarambagh Bridge";
  const float MOUNT_HEIGHT_CM = 200.0;  // Height of sensor from channel floor
  const float CAPACITY_CM     = 180.0;  // Max water depth before street overflow
#elif SELECTED_NODE == 2
  const char* NODE_ID = "drain-02";
  const char* LOCATION_NAME = "Chaderghat Causeway";
  const float MOUNT_HEIGHT_CM = 220.0;
  const float CAPACITY_CM     = 200.0;
#elif SELECTED_NODE == 3
  const char* NODE_ID = "drain-03";
  const char* LOCATION_NAME = "Amberpet Nallah";
  const float MOUNT_HEIGHT_CM = 180.0;
  const float CAPACITY_CM     = 150.0;
#else
  const char* NODE_ID = "drain-custom";
  const char* LOCATION_NAME = "Custom Sensor Node";
  const float MOUNT_HEIGHT_CM = 200.0;
  const float CAPACITY_CM     = 180.0;
#endif

// ============================================================================
// HARDWARE PIN ASSIGNMENTS
// ============================================================================
const int PIN_TRIG       = 5;
const int PIN_ECHO       = 18;
const int PIN_RAIN_ADC   = 34;   // ADC1 Channel 6
const int PIN_SERVO      = 19;
const int PIN_LED_RED    = 21;
const int PIN_LED_GREEN  = 22;
const int PIN_BUZZER     = 23;

// ============================================================================
// NETWORK & MQTT CONFIGURATION
// ============================================================================
const char* WIFI_SSID     = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// Default public HiveMQ broker (for Wokwi simulation) or configurable local broker
const char* MQTT_BROKER   = "broker.hivemq.com";
const int   MQTT_PORT     = 1883;

// MQTT Topics (derived from NODE_ID)
char topicTelemetry[64];
char topicStatus[64];
char topicCommand[64];

// ============================================================================
// GLOBAL OBJECTS & STATE VARIABLES
// ============================================================================
WiFiClient espClient;
PubSubClient mqttClient(espClient);
Servo floodgateServo;

// Current state
int currentGateAngle = 0;        // 0 = Open, 90 = Closed
float lastDepthCm = 0.0;
float lastRainRate = 0.0;
bool isCloudConnected = false;
bool isLocalAutonomyActive = false;

// Timing (Non-blocking state machine)
unsigned long lastTelemetryTime = 0;
unsigned long lastReconnectAttempt = 0;
unsigned long lastBuzzerToggle = 0;
bool buzzerState = false;

const unsigned long NORMAL_INTERVAL_MS = 10000;   // 10s normal cadence
const unsigned long ELEVATED_INTERVAL_MS = 2000;  // 2s rapid cadence when depth > 70%
unsigned long currentTelemetryInterval = NORMAL_INTERVAL_MS;

// Exponential reconnect backoff
unsigned long reconnectDelayMs = 2000;
const unsigned long MAX_RECONNECT_DELAY_MS = 30000;

// Base timestamp tracking for simulated unix time
unsigned long bootUnixTimestamp = 1731060000; // Simulated epoch baseline

// ============================================================================
// SENSOR FUNCTIONS
// ============================================================================

/**
 * Measure raw distance from HC-SR04 in centimeters with timeout.
 */
float readSingleDistanceCm() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duration = pulseIn(PIN_ECHO, HIGH, 26000); // ~4.5m max range timeout
  if (duration == 0) {
    return MOUNT_HEIGHT_CM; // Default to empty channel on timeout
  }
  return (float)duration * 0.0343f / 2.0f;
}

/**
 * 5-sample median filter to eliminate ultrasonic echoes and surface wave noise.
 */
float readMedianDistanceCm() {
  const int SAMPLES = 5;
  float readings[SAMPLES];

  for (int i = 0; i < SAMPLES; i++) {
    readings[i] = readSingleDistanceCm();
    delay(5); // Brief acoustic decay
  }

  // Simple insertion sort
  for (int i = 1; i < SAMPLES; i++) {
    float key = readings[i];
    int j = i - 1;
    while (j >= 0 && readings[j] > key) {
      readings[j + 1] = readings[j];
      j--;
    }
    readings[j + 1] = key;
  }

  return readings[SAMPLES / 2]; // Return median
}

/**
 * Read water depth in cm (Mount Height - Distance to Water Surface).
 */
float readWaterDepthCm() {
  float distance = readMedianDistanceCm();
  float depth = MOUNT_HEIGHT_CM - distance;
  if (depth < 0.0f) depth = 0.0f;
  if (depth > CAPACITY_CM) depth = CAPACITY_CM;
  return depth;
}

/**
 * Read simulated rain rate in mm/h from potentiometer ADC.
 */
float readRainRateMmH() {
  int rawAdc = analogRead(PIN_RAIN_ADC);
  // Linear scale 0-4095 -> 0.0 - 100.0 mm/h
  float rain = (float)rawAdc / 4095.0f * 100.0f;
  return rain;
}

// ============================================================================
// ACTUATION & ALARM FUNCTIONS
// ============================================================================

void setGateAngle(int angle, const char* reason) {
  if (angle < 0) angle = 0;
  if (angle > 90) angle = 90;
  currentGateAngle = angle;
  floodgateServo.write(currentGateAngle);
  Serial.print(F("[ACTUATE] Floodgate set to "));
  Serial.print(currentGateAngle);
  Serial.print(F(" deg. Reason: "));
  Serial.println(reason);
}

void updateIndicators(float depthCm, float capacityCm, bool connected) {
  float ratio = depthCm / capacityCm;

  // Green LED: Connectivity state
  digitalWrite(PIN_LED_GREEN, connected ? HIGH : LOW);

  // Red LED: Flood alert level
  if (ratio >= 0.85f) {
    // Critical: Rapid blink
    digitalWrite(PIN_LED_RED, (millis() / 250) % 2 == 0 ? HIGH : LOW);
  } else if (ratio >= 0.70f) {
    // Warning: Solid ON
    digitalWrite(PIN_LED_RED, HIGH);
  } else {
    // Normal/Watch: OFF
    digitalWrite(PIN_LED_RED, LOW);
  }
}

// ============================================================================
// MQTT & TELEMETRY
// ============================================================================

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  char message[256];
  if (length >= sizeof(message)) length = sizeof(message) - 1;
  memcpy(message, payload, length);
  message[length] = '\0';

  Serial.print(F("[MQTT CMD] Received on topic "));
  Serial.print(topic);
  Serial.print(F(": "));
  Serial.println(message);

  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, message);
  if (error) {
    Serial.print(F("[MQTT CMD ERR] Deserialization failed: "));
    Serial.println(error.c_str());
    return;
  }

  if (doc.containsKey("gate_angle")) {
    int targetAngle = doc["gate_angle"];
    const char* reason = doc.containsKey("reason") ? doc["reason"] : "cloud_command";
    setGateAngle(targetAngle, reason);
    // Cloud commands override local autonomy
    isLocalAutonomyActive = false;
  }
}

void publishTelemetry(float depthCm, float rainMmH) {
  StaticJsonDocument<256> doc;
  doc["node"]       = NODE_ID;
  doc["ts"]         = bootUnixTimestamp + (millis() / 1000);
  doc["depth_cm"]   = serialized(String(depthCm, 1));
  doc["rain_mm_h"]  = serialized(String(rainMmH, 1));
  doc["gate_deg"]   = currentGateAngle;
  doc["rssi"]       = WiFi.status() == WL_CONNECTED ? WiFi.RSSI() : -99;

  char buffer[256];
  serializeJson(doc, buffer);

  bool published = mqttClient.publish(topicTelemetry, buffer);
  Serial.print(F("[TELEMETRY] "));
  Serial.print(topicTelemetry);
  Serial.print(F(" -> "));
  Serial.print(buffer);
  Serial.println(published ? F(" (OK)") : F(" (FAILED)"));
}

bool connectMqtt() {
  char clientId[48];
  snprintf(clientId, sizeof(clientId), "esp32-flood-%s-%04X", NODE_ID, (uint16_t)random(0xFFFF));

  // LWT configuration: retained "offline" to status topic with QoS 1
  const char* willTopic = topicStatus;
  const int willQos = 1;
  const bool willRetain = true;
  const char* willMessage = "offline";

  Serial.print(F("[MQTT] Attempting broker connection to "));
  Serial.print(MQTT_BROKER);
  Serial.print(F(" as "));
  Serial.println(clientId);

  if (mqttClient.connect(clientId, willTopic, willQos, willRetain, willMessage)) {
    Serial.println(F("[MQTT] Connected successfully!"));

    // Publish retained "online"
    mqttClient.publish(topicStatus, "online", true);

    // Subscribe to node command topic
    mqttClient.subscribe(topicCommand);
    Serial.print(F("[MQTT] Subscribed to "));
    Serial.println(topicCommand);

    reconnectDelayMs = 2000; // Reset backoff on success
    return true;
  } else {
    Serial.print(F("[MQTT] Connect failed, rc="));
    Serial.println(mqttClient.state());
    return false;
  }
}

// ============================================================================
// SETUP & MAIN LOOP
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println(F("\n=============================================="));
  Serial.println(F("   flood-ews Smart Drainage Early Warning     "));
  Serial.println(F("=============================================="));
  Serial.print(F("Node ID: ")); Serial.println(NODE_ID);
  Serial.print(F("Location: ")); Serial.println(LOCATION_NAME);
  Serial.print(F("Mount Height: ")); Serial.print(MOUNT_HEIGHT_CM); Serial.println(F(" cm"));
  Serial.print(F("Capacity: ")); Serial.print(CAPACITY_CM); Serial.println(F(" cm"));

  // Build topic strings
  snprintf(topicTelemetry, sizeof(topicTelemetry), "flood/v1/%s/telemetry", NODE_ID);
  snprintf(topicStatus, sizeof(topicStatus), "flood/v1/%s/status", NODE_ID);
  snprintf(topicCommand, sizeof(topicCommand), "flood/v1/%s/cmd", NODE_ID);

  // Pin modes
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_RAIN_ADC, INPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  digitalWrite(PIN_TRIG, LOW);
  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_LED_RED, LOW);
  digitalWrite(PIN_BUZZER, LOW);

  // Initialize Servo
  floodgateServo.setPeriodHertz(50); // Standard 50Hz servo
  floodgateServo.attach(PIN_SERVO, 500, 2400); // 500us to 2400us pulse widths
  setGateAngle(0, "boot_initialization");

  // Connect Wi-Fi
  Serial.print(F("[WIFI] Connecting to "));
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  // MQTT Client setup
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  mqttClient.setBufferSize(512);

  randomSeed(micros());
}

void loop() {
  unsigned long now = millis();

  // 1. Manage Wi-Fi & MQTT Connectivity
  bool wifiOk = (WiFi.status() == WL_CONNECTED);
  bool mqttOk = mqttClient.connected();
  isCloudConnected = wifiOk && mqttOk;

  if (isCloudConnected) {
    mqttClient.loop();
  } else {
    // Non-blocking reconnect with exponential backoff
    if (now - lastReconnectAttempt > reconnectDelayMs) {
      lastReconnectAttempt = now;
      if (wifiOk) {
        if (!mqttOk) {
          if (connectMqtt()) {
            isCloudConnected = true;
          } else {
            reconnectDelayMs = min(reconnectDelayMs * 2, MAX_RECONNECT_DELAY_MS);
          }
        }
      } else {
        Serial.println(F("[WIFI] Reconnecting..."));
        WiFi.reconnect();
      }
    }
  }

  // 2. Read Sensors
  lastDepthCm = readWaterDepthCm();
  lastRainRate = readRainRateMmH();
  float depthRatio = lastDepthCm / CAPACITY_CM;

  // 3. Adaptive Telemetry Rate: 10s normal, 2s if depth > 70% of capacity
  currentTelemetryInterval = (depthRatio > 0.70f) ? ELEVATED_INTERVAL_MS : NORMAL_INTERVAL_MS;

  if (now - lastTelemetryTime >= currentTelemetryInterval) {
    lastTelemetryTime = now;
    if (isCloudConnected) {
      publishTelemetry(lastDepthCm, lastRainRate);
    }
  }

  // 4. LOCAL AUTONOMY: When disconnected from cloud & depth > 85%, close gate and sound alarm
  if (!isCloudConnected && depthRatio > 0.85f) {
    if (!isLocalAutonomyActive) {
      isLocalAutonomyActive = true;
      Serial.println(F("[AUTONOMY ALERT] Cloud disconnected & depth > 85%! Emergency gate closure."));
      setGateAngle(90, "local_autonomy_critical");
    }
    // Alarm siren pulse
    if (now - lastBuzzerToggle > 200) {
      lastBuzzerToggle = now;
      buzzerState = !buzzerState;
      digitalWrite(PIN_BUZZER, buzzerState ? HIGH : LOW);
    }
  } else {
    if (isLocalAutonomyActive && isCloudConnected) {
      // Cloud reconnected, allow cloud to control
      isLocalAutonomyActive = false;
    }
    // Turn off buzzer if not in autonomous emergency
    if (!isLocalAutonomyActive) {
      digitalWrite(PIN_BUZZER, LOW);
    }
  }

  // 5. Update Status LEDs
  updateIndicators(lastDepthCm, CAPACITY_CM, isCloudConnected);

  // Brief yield for RTOS tasks
  delay(10);
}
