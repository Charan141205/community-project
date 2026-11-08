import time
import network
import ujson
from machine import Pin, PWM, ADC
from machine import time_pulse_us

# ============================================================================
# HARDWARE PIN DEFINITIONS (Matching diagram.json)
# ============================================================================
TRIG_PIN = 5
ECHO_PIN = 18
SERVO_PIN = 19
LED_RED_PIN = 21
LED_GREEN_PIN = 22
BUZZER_PIN = 23
POT_PIN = 34

# ============================================================================
# PHYSICAL DRAIN CONSTANTS (Tirupati Flashpoint: drain-01)
# ============================================================================
MOUNT_HEIGHT_CM = 200.0  # Sensor mount height above channel floor
MAX_DRAIN_DEPTH = 180.0  # Max depth before flooding (180 cm)
NODE_ID = "drain-01"

# ============================================================================
# PIN & PERIPHERAL INITIALIZATIONS
# ============================================================================
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)
trig.value(0)

led_red = Pin(LED_RED_PIN, Pin.OUT)
led_green = Pin(LED_GREEN_PIN, Pin.OUT)
buzzer = Pin(BUZZER_PIN, Pin.OUT)

led_green.value(1)  # Green ON (Normal)
led_red.value(0)
buzzer.value(0)

pot = ADC(Pin(POT_PIN))
pot.atten(ADC.ATTN_11DB)  # 0 - 3.3V range

# Native ESP32 Hardware PWM for SG90 Servo (50Hz)
servo = PWM(Pin(SERVO_PIN), freq=50)

def set_gate_angle(deg):
    deg = max(0, min(180, deg))
    # SG90 standard: 500us (0 deg) to 2400us (180 deg) out of 20000us period
    pulse_us = 500 + (deg * (2400 - 500) // 180)
    duty = int((pulse_us / 20000.0) * 65535)
    servo.duty_u16(duty)

set_gate_angle(0)  # Start with gate open (0 deg)

# ============================================================================
# SENSOR READ FUNCTIONS (5-Sample Median Filter)
# ============================================================================
def read_distance_cm():
    samples = []
    for _ in range(5):
        trig.value(0)
        time.sleep_us(2)
        trig.value(1)
        time.sleep_us(10)
        trig.value(0)
        
        try:
            duration = time_pulse_us(echo, 1, 30000)
            if duration <= 0:
                dist = MOUNT_HEIGHT_CM
            else:
                dist = (duration * 0.0343) / 2.0
        except OSError:
            dist = MOUNT_HEIGHT_CM
        samples.append(dist)
        time.sleep_ms(5)
    
    samples.sort()
    return samples[2]  # Median value

def read_rain_mm_h():
    raw = pot.read()
    return round((raw / 4095.0) * 100.0, 1)

# ============================================================================
# NETWORK & MQTT CONFIGURATION (HiveMQ Public Broker)
# ============================================================================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_TELEMETRY = "flood/v1/drain-01/telemetry"
TOPIC_TELEMETRY_EWS = "ews/telemetry/drain-01"
TOPIC_CMD = "flood/v1/drain-01/cmd"
TOPIC_STATUS = "flood/v1/drain-01/status"

client = None

def mqtt_callback(topic, msg):
    global current_gate_angle
    try:
        data = ujson.loads(msg.decode())
        target = data.get("gate_angle", data.get("gate_deg", -1))
        if target >= 0:
            target = max(0, min(90, target))
            current_gate_angle = target
            set_gate_angle(current_gate_angle)
            print(f"[SCADA COMMAND] Remote Gate Angle: {current_gate_angle} deg")
    except Exception as e:
        print("[MQTT] Callback parse error:", e)

def connect_network():
    global client
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("[WIFI] Connecting to Wokwi-GUEST...")
        wlan.connect("Wokwi-GUEST", "")
        t0 = time.time()
        while not wlan.isconnected() and (time.time() - t0 < 6):
            time.sleep_ms(250)
    
    if wlan.isconnected():
        print("[WIFI] Connected! IP:", wlan.ifconfig()[0])
        try:
            from umqtt.simple import MQTTClient
            client = MQTTClient("drain-01-wokwi", MQTT_BROKER, port=MQTT_PORT)
            client.set_callback(mqtt_callback)
            client.connect()
            client.subscribe(TOPIC_CMD)
            client.publish(TOPIC_STATUS, b"online", retain=True)
            print("[MQTT] Connected to HiveMQ Broker!")
        except Exception as e:
            print("[MQTT] Connection bypassed:", e)
            client = None

try:
    connect_network()
except Exception as e:
    print("[INIT] Network warning:", e)

# ============================================================================
# MAIN LOOP (Instant Slider Responsiveness)
# ============================================================================
print("==================================================")
print("  flood-ews MicroPython Node Ready!")
print("  Drag HC-SR04 distance slider to test!")
print("==================================================")

current_gate_angle = 0
last_distance = -1.0
last_publish = time.time()

while True:
    if client:
        try:
            client.check_msg()
        except Exception:
            pass

    # Read Sensors
    dist_cm = read_distance_cm()
    water_depth_cm = max(0.0, min(MAX_DRAIN_DEPTH, MOUNT_HEIGHT_CM - dist_cm))
    fill_pct = (water_depth_cm / MAX_DRAIN_DEPTH) * 100.0
    rain_rate = read_rain_mm_h()

    # Edge Autonomy:
    # Fill >= 70% (Distance <= 74cm): Red LED ON, Siren ON, Gate 90 deg (Closed)
    # Fill <= 50% (Distance >= 110cm): Green LED ON, Siren OFF, Gate 0 deg (Open)
    if fill_pct >= 70.0:
        current_gate_angle = 90
        led_red.value(1)
        led_green.value(0)
        buzzer.value(1)
    elif fill_pct <= 50.0:
        current_gate_angle = 0
        led_red.value(0)
        led_green.value(1)
        buzzer.value(0)

    # Actuate SG90 Servo
    set_gate_angle(current_gate_angle)

    # Publish Telemetry on Slider Shift (>= 5cm difference) or Timer (every 3s)
    now = time.time()
    if abs(dist_cm - last_distance) >= 5.0 or (now - last_publish >= 3):
        last_distance = dist_cm
        last_publish = now
        print(f"[SENSOR] Distance: {dist_cm:.1f} cm | Depth: {water_depth_cm:.1f} cm ({fill_pct:.1f}%) -> Gate: {current_gate_angle} deg")

        if client:
            payload = ujson.dumps({
                "node": NODE_ID,
                "node_id": NODE_ID,
                "depth_cm": round(water_depth_cm, 1),
                "water_depth_cm": round(water_depth_cm, 1),
                "fill_percentage": round(fill_pct, 1),
                "ratio": round(fill_pct / 100.0, 2),
                "rain_mm_h": rain_rate,
                "gate_deg": current_gate_angle,
                "gate_angle": current_gate_angle,
                "ts": int(now)
            })
            try:
                client.publish(TOPIC_TELEMETRY, payload.encode())
                client.publish(TOPIC_TELEMETRY_EWS, payload.encode())
            except Exception:
                pass

    time.sleep_ms(50)  # 50ms cycle for instant UI response
