/**
 * flood-ews: Smart Community Flood & Urban Drainage Early Warning System
 * Production ESP32 Firmware with Dual Wokwi/Hardware Support & ESP-NOW Mesh Fallback
 *
 * SENSORS & ACTUATORS:
 * - HC-SR04 Ultrasonic Distance Sensor: Water level in drain channel
 * - Potentiometer / Tipping Bucket (ADC GPIO34): Precipitation rate (0.0 to 100.0 mm/h)
 * - Micro Servo (GPIO19): Floodgate Actuator (0 deg = FULLY OPEN, 90 deg = FULLY CLOSED)
 * - Green LED (GPIO22): System/Connectivity Status (MQTT Online)
 * - Red LED (GPIO21): Warning/Critical Flood Indicator
 * - Buzzer (GPIO23): Local Autonomous Emergency Siren
 *
 * RESILIENCE FEATURES:
 * 1. 5-sample median ultrasonic noise filter
 * 2. Adaptive telemetry cadence (10s normal / 2s rapid flood alert)
 * 3. Local Autonomy: Failsafe gate closure & siren if disconnected & depth > 85%
 * 4. ESP-NOW Hardware Mesh Fallback: Relays telemetry peer-to-peer if Wi-Fi drops
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>
#include <esp_now.h>
#include <esp_wifi.h>

// ============================================================================
// ENVIRONMENT SELECTOR: Set to true for Wokwi virtual simulation, false for Physical Hardware
// ============================================================================
#define USE_WOKWI_SIMULATION true

// ============================================================================
// NODE PRESET SELECTION (Change SELECTED_NODE to 1, 2, or 3)
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
// HARDWARE PIN ASSIGNMENTS (Customizable per physical shield layout)
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
#if USE_WOKWI_SIMULATION
  const char* WIFI_SSID     = "Wokwi-GUEST";
  const char* WIFI_PASSWORD = "";
  const char* MQTT_BROKER   = "broker.hivemq.com";
  const int   MQTT_PORT     = 1883;
  const char* MQTT_USER     = "";
  const char* MQTT_PASSWORD = "";
#else
  // Production Hardware Credentials (Set your local/production network details)
  const char* WIFI_SSID     = "PROD_SMART_CITY_IOT";
  const char* WIFI_PASSWORD = "StrongSecurePassword123";
  const char* MQTT_BROKER   = "mqtt.yourdomain.com"; // or AWS IoT / HiveMQ Cloud
  const int   MQTT_PORT     = 1883;
  const char* MQTT_USER     = "flood_operator";
  const char* MQTT_PASSWORD = "MqttOperatorSecret!";
#endif

// MQTT Topics
char topicTelemetry[64];
char topicStatus[64];
char topicCommand[64];

// ============================================================================
// ESP-NOW MESH PEER-TO-PEER DATA STRUCTURE
// ============================================================================
typedef struct __attribute__((packed)) {
  char node_id[16];
  uint32_t ts;
  float depth_cm;
  float rain_mm_h;
  uint8_t gate_deg;
  int8_t rssi;
} FloodMeshPacket;

// Broadcast MAC address (FF:FF:FF:FF:FF:FF)
uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
bool isMeshActive = false;

// ============================================================================
// GLOBAL OBJECTS & STATE
// ============================================================================
WiFiClient espClient;
PubSubClient mqttClient(espClient);
Servo floodgateServo;

int currentGateAngle = 0;        // 0 = Open, 90 = Closed
float lastDepthCm = 0.0;
float lastRainRate = 0.0;
bool isCloudConnected = false;
bool isLocalAutonomyActive = false;

unsigned long lastTelemetryTime = 0;
unsigned long lastReconnectAttempt = 0;
unsigned long lastBuzzerToggle = 0;
unsigned long lastMeshBeaconTime = 0;
bool buzzerState = false;

const unsigned long NORMAL_INTERVAL_MS = 10000;   // 10s normal cadence
const unsigned long ELEVATED_INTERVAL_MS = 2000;  // 2s rapid cadence when depth > 70%
unsigned long currentTelemetryInterval = NORMAL_INTERVAL_MS;

unsigned long reconnectDelayMs = 2000;
const unsigned long MAX_RECONNECT_DELAY_MS = 30000;
unsigned long bootUnixTimestamp = 1731060000;

// ============================================================================
// ESP-NOW MESH RELAY CALLBACK
// ============================================================================
void onDataRecv(const uint8_t *mac_addr, const uint8_t *incomingData, int len) {
  if (len == sizeof(FloodMeshPacket)) {
    FloodMeshPacket packet;
    memcpy(&packet, incomingData, sizeof(packet));

    Serial.print(F("[ESP-NOW MESH] Received relay packet from "));
    Serial.println(packet.node_id);

    // If this node has active Wi-Fi and MQTT, relay the neighbor's packet to cloud!
    if (mqttClient.connected()) {
      StaticJsonDocument<256> doc;
      doc["node"]        = packet.node_id;
      doc["ts"]          = packet.ts;
      doc["depth_cm"]    = serialized(String(packet.depth_cm, 1));
      doc["rain_mm_h"]   = serialized(String(packet.rain_mm_h, 1));
      doc["gate_deg"]    = packet.gate_deg;
      doc["rssi"]        = packet.rssi;
      doc["mesh_relayed"]= true;

      char buffer[256];
      serializeJson(doc, buffer);
      char relayTopic[64];
      snprintf(relayTopic, sizeof(relayTopic), "flood/v1/%s/telemetry", packet.node_id);
      mqttClient.publish(relayTopic, buffer);
      Serial.print(F("[MESH BRIDGE -> MQTT] Relayed: "));
      Serial.println(buffer);
    }
  }
}

void initEspNowMesh() {
  if (esp_now_init() == ESP_OK) {
    isMeshActive = true;
    esp_now_register_recv_cb(onDataRecv);

    esp_now_peer_info_t peerInfo = {};
    memcpy(peerInfo.peer_addr, broadcastAddress, 6);
    peerInfo.channel = 0;
    peerInfo.encrypt = false;
    esp_now_add_peer(&peerInfo);
    Serial.println(F("[ESP-NOW MESH] Initialized peer-to-peer relay fallback."));
  }
}

// ============================================================================
// SENSOR FUNCTIONS
// ============================================================================

float readSingleDistanceCm() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duration = pulseIn(PIN_ECHO, HIGH, 26000); // ~4.5m timeout
  if (duration == 0) return MOUNT_HEIGHT_CM;
  return (float)duration * 0.0343f / 2.0f;
}

float readMedianDistanceCm() {
  const int SAMPLES = 5;
  float readings[SAMPLES];

  for (int i = 0; i < SAMPLES; i++) {
    readings[i] = readSingleDistanceCm();
    delay(5);
  }

  // Insertion sort
  for (int i = 1; i < SAMPLES; i++) {
    float key = readings[i];
    int j = i - 1;
    while (j >= 0 && readings[j] > key) {
      readings[j + 1] = readings[j];
      j--;
    }
    readings[j + 1] = key;
  }

  return readings[SAMPLES / 2];
}

float readWaterDepthCm() {
  float distance = readMedianDistanceCm();
  float depth = MOUNT_HEIGHT_CM - distance;
  if (depth < 0.0f) depth = 0.0f;
  if (depth > CAPACITY_CM) depth = CAPACITY_CM;
  return depth;
}

float readRainRateMmH() {
  int rawAdc = analogRead(PIN_RAIN_ADC);
  return (float)rawAdc / 4095.0f * 100.0f;
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

  digitalWrite(PIN_LED_GREEN, connected ? HIGH : LOW);

  if (ratio >= 0.85f) {
    digitalWrite(PIN_LED_RED, (millis() / 250) % 2 == 0 ? HIGH : LOW);
  } else if (ratio >= 0.70f) {
    digitalWrite(PIN_LED_RED, HIGH);
  } else {
    digitalWrite(PIN_LED_RED, LOW);
  }
}

// ============================================================================
// MQTT CALLBACK & TELEMETRY
// ============================================================================

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  char message[256];
  if (length >= sizeof(message)) length = sizeof(message) - 1;
  memcpy(message, payload, length);
  message[length] = '\0';

  Serial.print(F("[MQTT CMD] Received on "));
  Serial.print(topic);
  Serial.print(F(": "));
  Serial.println(message);

  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, message);
  if (!error && doc.containsKey("gate_angle")) {
    int targetAngle = doc["gate_angle"];
    const char* reason = doc.containsKey("reason") ? doc["reason"] : "cloud_command";
    setGateAngle(targetAngle, reason);
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

void broadcastEspNowMesh(float depthCm, float rainMmH) {
  if (!isMeshActive) return;

  FloodMeshPacket packet;
  strncpy(packet.node_id, NODE_ID, sizeof(packet.node_id) - 1);
  packet.ts = bootUnixTimestamp + (millis() / 1000);
  packet.depth_cm = depthCm;
  packet.rain_mm_h = rainMmH;
  packet.gate_deg = (uint8_t)currentGateAngle;
  packet.rssi = -80;

  esp_now_send(broadcastAddress, (uint8_t *)&packet, sizeof(packet));
  Serial.println(F("[ESP-NOW MESH] Broadcasted peer-to-peer packet to neighbors."));
}

bool connectMqtt() {
  char clientId[48];
  snprintf(clientId, sizeof(clientId), "esp32-flood-%s-%04X", NODE_ID, (uint16_t)random(0xFFFF));

  const char* willTopic = topicStatus;
  const int willQos = 1;
  const bool willRetain = true;
  const char* willMessage = "offline";

  Serial.print(F("[MQTT] Connecting to "));
  Serial.print(MQTT_BROKER);
  Serial.print(F(" as "));
  Serial.println(clientId);

  bool ok = false;
  if (strlen(MQTT_USER) > 0) {
    ok = mqttClient.connect(clientId, MQTT_USER, MQTT_PASSWORD, willTopic, willQos, willRetain, willMessage);
  } else {
    ok = mqttClient.connect(clientId, willTopic, willQos, willRetain, willMessage);
  }

  if (ok) {
    Serial.println(F("[MQTT] Connected successfully!"));
    mqttClient.publish(topicStatus, "online", true);
    mqttClient.subscribe(topicCommand);
    reconnectDelayMs = 2000;
    return true;
  } else {
    Serial.print(F("[MQTT] Connect failed, state="));
    Serial.println(mqttClient.state());
    return false;
  }
}

// ============================================================================
// SETUP & LOOP
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println(F("\n=============================================="));
  Serial.println(F("   flood-ews Production IoT Early Warning Node "));
  Serial.println(F("=============================================="));
  Serial.print(F("Node ID: ")); Serial.println(NODE_ID);
  Serial.print(F("Location: ")); Serial.println(LOCATION_NAME);
  Serial.print(F("Mount Height: ")); Serial.print(MOUNT_HEIGHT_CM); Serial.println(F(" cm"));
  Serial.print(F("Capacity: ")); Serial.print(CAPACITY_CM); Serial.println(F(" cm"));
  Serial.print(F("Simulation Mode: ")); Serial.println(USE_WOKWI_SIMULATION ? F("Wokwi Virtual") : F("Physical Production"));

  snprintf(topicTelemetry, sizeof(topicTelemetry), "flood/v1/%s/telemetry", NODE_ID);
  snprintf(topicStatus, sizeof(topicStatus), "flood/v1/%s/status", NODE_ID);
  snprintf(topicCommand, sizeof(topicCommand), "flood/v1/%s/cmd", NODE_ID);

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

  floodgateServo.setPeriodHertz(50);
  floodgateServo.attach(PIN_SERVO, 500, 2400);
  setGateAngle(0, "boot_initialization");

  // Initialize Wi-Fi in Station Mode
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  // Initialize ESP-NOW Mesh Fallback
  initEspNowMesh();

  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  mqttClient.setBufferSize(512);

  randomSeed(micros());
}

void loop() {
  unsigned long now = millis();

  bool wifiOk = (WiFi.status() == WL_CONNECTED);
  bool mqttOk = mqttClient.connected();
  isCloudConnected = wifiOk && mqttOk;

  if (isCloudConnected) {
    mqttClient.loop();
  } else {
    // Non-blocking reconnect
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

  // Read Sensors
  lastDepthCm = readWaterDepthCm();
  lastRainRate = readRainRateMmH();
  float depthRatio = lastDepthCm / CAPACITY_CM;

  // Adaptive interval: 10s normal / 2s when depth > 70%
  currentTelemetryInterval = (depthRatio > 0.70f) ? ELEVATED_INTERVAL_MS : NORMAL_INTERVAL_MS;

  if (now - lastTelemetryTime >= currentTelemetryInterval) {
    lastTelemetryTime = now;
    if (isCloudConnected) {
      publishTelemetry(lastDepthCm, lastRainRate);
    } else {
      // Wi-Fi or MQTT disconnected: Broadcast via ESP-NOW Mesh peer-to-peer!
      broadcastEspNowMesh(lastDepthCm, lastRainRate);
    }
  }

  // Local Autonomy Failsafe: Disconnected & depth > 85% -> auto-close gate & pulse siren
  if (!isCloudConnected && depthRatio > 0.85f) {
    if (!isLocalAutonomyActive) {
      isLocalAutonomyActive = true;
      Serial.println(F("[AUTONOMY FAILSAFE] Disconnected & depth > 85%! Emergency gate closure."));
      setGateAngle(90, "local_autonomy_critical");
    }
    if (now - lastBuzzerToggle > 200) {
      lastBuzzerToggle = now;
      buzzerState = !buzzerState;
      digitalWrite(PIN_BUZZER, buzzerState ? HIGH : LOW);
    }
  } else {
    if (isLocalAutonomyActive && isCloudConnected) {
      isLocalAutonomyActive = false;
    }
    if (!isLocalAutonomyActive) {
      digitalWrite(PIN_BUZZER, LOW);
    }
  }

  updateIndicators(lastDepthCm, CAPACITY_CM, isCloudConnected);
  delay(10);
}
