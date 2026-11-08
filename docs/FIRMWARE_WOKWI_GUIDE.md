# ESP32 Firmware & Wokwi Simulation Guide

This document details the hardware configuration, pinout assignments, algorithm design, and simulation steps for the ESP32 stormwater drainage sensor node.

---

## 1. Hardware Pinout & Wiring

| Component | ESP32 Pin | Function |
|---|---|---|
| **HC-SR04 Trig** | GPIO 5 (Output) | 10µs ultrasonic trigger pulse |
| **HC-SR04 Echo** | GPIO 18 (Input) | Ultrasonic return pulse timing (30ms timeout) |
| **Potentiometer** | GPIO 34 (ADC1_CH6) | Simulated rain gauge (0.0 to 100.0 mm/h) |
| **Micro Servo** | GPIO 19 (PWM) | Floodgate actuator: 0° (Open) to 90° (Closed) |
| **Green LED** | GPIO 22 (Output) | Wi-Fi / MQTT Online indicator |
| **Red LED** | GPIO 21 (Output) | Warning (solid) / Critical (pulsing) alert indicator |
| **Active Buzzer**| GPIO 23 (Output) | Emergency failsafe alarm siren |

---

## 2. Running in Wokwi (Browser)

1. Navigate to [Wokwi ESP32 Web Simulator](https://wokwi.com/projects/new/esp32).
2. Replace `sketch.ino` with the contents of [`firmware/sketch.ino`](../firmware/sketch.ino).
3. Replace `diagram.json` with the contents of [`firmware/diagram.json`](../firmware/diagram.json).
4. In the **Libraries** tab, add:
   - `PubSubClient`
   - `ESP32Servo`
   - `ArduinoJson`
5. Click **Start Simulation**.
6. Move the potentiometer wiper to simulate increasing rainfall intensity.
7. Click the HC-SR04 sensor and drag the target to simulate rising water level.

---

## 3. Running in VS Code (Wokwi Extension)

1. Install the official **Wokwi Simulator** extension from the VS Code Marketplace.
2. Open [`firmware/diagram.json`](../firmware/diagram.json) in VS Code.
3. Press `F1` (or `Ctrl+Shift+P`) and choose **Wokwi: Start Simulator**.

---

## 4. Node Switching & Presets

The firmware contains built-in configurations for 3 primary flood flashpoints along Hyderabad's Musi River. Change `#define SELECTED_NODE` at the top of [`firmware/sketch.ino`](../firmware/sketch.ino):

```cpp
#define SELECTED_NODE 1  // 1: Moosarambagh Bridge, 2: Chaderghat Causeway, 3: Amberpet Nallah
```

| Preset | Node ID | Location | Mount Height | Capacity |
|---|---|---|---|---|
| 1 | `drain-01` | Moosarambagh Bridge | 200 cm | 180 cm |
| 2 | `drain-02` | Chaderghat Causeway | 220 cm | 200 cm |
| 3 | `drain-03` | Amberpet Nallah | 180 cm | 150 cm |

---

## 5. Local Autonomy Failsafe Test

1. In Wokwi, change the Wi-Fi SSID to an invalid name to simulate communication failure.
2. Adjust the ultrasonic distance sensor so water depth exceeds 85% of capacity.
3. Observe:
   - The green LED turns off (cloud offline).
   - The red LED pulses rapidly.
   - The floodgate servo automatically actuates to **90° (Closed)**.
   - The buzzer sounds an emergency audio siren.
4. Restore connectivity; cloud commands automatically resume control without requiring a node reboot.
