import time
import network
import ujson
from machine import Pin, PWM, ADC
from machine import time_pulse_us
from umqtt.simple import MQTTClient

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

MOUNT_HEIGHT_CM = 200.0  # Sensor mount height above channel floor
MAX_DRAIN_DEPTH = 180.0  # Max channel overflow depth before flood (180 cm)
NODE_ID = "drain-01"

# ============================================================================
# PIN & PERIPHERAL INITIALIZATION
# ============================================================================
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)
trig.value(0)

led_red = Pin(LED_RED_PIN, Pin.OUT)
led_green = Pin(LED_GREEN_PIN, Pin.OUT)
buzzer = Pin(BUZZER_PIN, Pin.OUT)

led_green.value(1)  # Green LED ON (Normal)
led_red.value(0)
buzzer.value(0)

pot = ADC(Pin(POT_PIN))
pot.atten(ADC.ATTN_11DB)  # Full 0 - 3.3V range

# Native Hardware PWM for SG90 Servo (50Hz)
servo = PWM(Pin(SERVO_PIN), freq=50)

def set_gate_angle(deg):
    deg = max(0, min(180, deg))
    pulse_us = 500 + (deg * (2400 - 500) // 180)
    duty = int((pulse_us / 20000.0) * 65535)
    servo.duty_u16(duty)

set_gate_angle(0)  # Start with gate open (0 deg)

# ============================================================================
# WI-FI & HIVEMQ MQTT CONNECTION
# ============================================================================
print("[WIFI] Connecting to Wokwi-GUEST...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Wokwi-GUEST", "")

while not wlan.isconnected():
    time.sleep_ms(200)

print("[WIFI] Connected! IP:", wlan.ifconfig()[0])

MQTT_BROKER = "broker.hivemq.com"
TOPIC_TELEMETRY = "flood/v1/drain-01/telemetry"
TOPIC_CMD = "flood/v1/drain-01/cmd"
TOPIC_STATUS = "flood/v1/drain-01/status"

current_gate_angle = 0

def mqtt_callback(topic, msg):
    global current_gate_angle
    try:
        data = ujson.loads(msg.decode())
        target = data.get("gate_angle", data.get("gate_deg", -1))
        if target >= 0:
            current_gate_angle = max(0, min(90, target))
            set_gate_angle(current_gate_angle)
            print(f"[SCADA COMMAND] Remote Gate Angle: {current_gate_angle}°")
    except Exception as e:
        print("[MQTT] Parse error:", e)

print("[MQTT] Connecting to HiveMQ broker...")
client_id = f"wokwi-drain01-{time.ticks_ms()}"
client = MQTTClient(client_id, MQTT_BROKER, port=1883, keepalive=60)
client.set_callback(mqtt_callback)
client.connect()
client.subscribe(TOPIC_CMD)
client.publish(TOPIC_STATUS, b"online", retain=True)
print("[MQTT] CONNECTED! Live Telemetry Active to Dashboard.")

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
            dur = time_pulse_us(echo, 1, 30000)
            dist = (dur * 0.0343) / 2.0 if dur > 0 else MOUNT_HEIGHT_CM
        except OSError:
            dist = MOUNT_HEIGHT_CM
        samples.append(dist)
        time.sleep_ms(5)
    samples.sort()
    return samples[2]

def read_rain_mm_h():
    return round((pot.read() / 4095.0) * 100.0, 1)

# ============================================================================
# MAIN LOOP
# ============================================================================
print("==================================================")
print("  flood-ews MicroPython Node Running Live!")
print("  Drag HC-SR04 distance slider in Wokwi!")
print("==================================================")

last_distance = -1.0
last_publish = time.time()

while True:
    try:
        client.check_msg()
    except Exception:
        pass

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

    # Publish Telemetry on slider move (>= 3cm) or every 2 seconds
    now = time.time()
    if abs(dist_cm - last_distance) >= 3.0 or (now - last_publish >= 2):
        last_distance = dist_cm
        last_publish = now
        print(f"[SENSOR] Distance: {dist_cm:.1f} cm | Depth: {water_depth_cm:.1f} cm ({fill_pct:.1f}%) -> Gate: {current_gate_angle}°")

        payload = ujson.dumps({
            "node": NODE_ID,
            "ts": int(now),
            "depth_cm": round(water_depth_cm, 1),
            "rain_mm_h": rain_rate,
            "gate_deg": current_gate_angle,
            "rssi": -65
        })
        try:
            client.publish(TOPIC_TELEMETRY, payload)
        except Exception as e:
            print("[MQTT] Publish retry:", e)

    time.sleep_ms(50)  # 50ms cycle for instant UI responsiveness
