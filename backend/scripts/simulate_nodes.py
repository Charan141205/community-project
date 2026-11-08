#!/usr/bin/env python3
"""
flood-ews Node Telemetry Simulator
Simulates 6 ESP32 drainage sensor nodes across Tirupati Swarnamukhi basin and foothill flashpoints.
Supports continuous simulation and scripted scenarios (storm, normal, watch, critical).
"""

import argparse
import json
import logging
import math
import os
import random
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("[ERROR] paho-mqtt is required. Run: pip install paho-mqtt")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("simulate_nodes")

# ============================================================================
# NODE DEFINITIONS (Tirupati Swarnamukhi Basin & Seshachalam Foothills)
# ============================================================================
@dataclass
class SimulatedNode:
    id: str
    name: str
    lat: float
    lon: float
    ward: str
    mount_height_cm: float
    capacity_cm: float
    depth_cm: float = 25.0
    rain_mm_h: float = 0.0
    gate_deg: int = 0
    rssi: int = -65
    last_published: float = 0.0
    last_cmd_reason: str = ""

NODES: List[SimulatedNode] = [
    SimulatedNode("drain-01", "Kapilatheertham Nallah", 13.6508, 79.4215, "Alipiri", 200.0, 180.0, depth_cm=35.0),
    SimulatedNode("drain-02", "Leela Mahal Culvert", 13.6370, 79.4285, "Korlagunta", 220.0, 200.0, depth_cm=40.0),
    SimulatedNode("drain-03", "Railway Underbridge (West)", 13.6255, 79.4205, "Tata Nagar", 180.0, 150.0, depth_cm=28.0),
    SimulatedNode("drain-04", "Korlagunta Storm Canal", 13.6330, 79.4350, "Korlagunta", 210.0, 190.0, depth_cm=32.0),
    SimulatedNode("drain-05", "Alipiri Footpath Channel", 13.6450, 79.4070, "Alipiri", 190.0, 160.0, depth_cm=26.0),
    SimulatedNode("drain-06", "Tiruchanur Swarnamukhi Causeway", 13.6095, 79.4505, "Tiruchanur", 230.0, 210.0, depth_cm=45.0),
]

node_map: Dict[str, SimulatedNode] = {n.id: n for n in NODES}

# ============================================================================
# MQTT HANDLERS
# ============================================================================
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info("Connected to MQTT broker successfully.")
        # Subscribe to all command topics: flood/v1/+/cmd
        client.subscribe("flood/v1/+/cmd")
        logger.info("Subscribed to command topics: flood/v1/+/cmd")
        # Publish initial retained status for all nodes
        for node in NODES:
            topic_status = f"flood/v1/{node.id}/status"
            client.publish(topic_status, "online", qos=1, retain=True)
    else:
        logger.error(f"Failed to connect to MQTT broker, return code {rc}")

def on_message(client, userdata, msg):
    try:
        topic_parts = msg.topic.split("/")
        if len(topic_parts) >= 4 and topic_parts[3] == "cmd":
            node_id = topic_parts[2]
            payload = json.loads(msg.payload.decode("utf-8"))
            logger.warning(f"⚡ RECEIVED ACTUATION COMMAND for [{node_id}]: {payload}")
            if node_id in node_map:
                node = node_map[node_id]
                if "gate_angle" in payload:
                    node.gate_deg = int(payload["gate_angle"])
                    node.last_cmd_reason = payload.get("reason", "manual")
                    logger.info(f"🚪 Node [{node_id}] Floodgate moved to {node.gate_deg}° (Reason: {node.last_cmd_reason})")
    except Exception as e:
        logger.error(f"Error parsing MQTT command: {e}")

# ============================================================================
# SCENARIO RUNNER
# ============================================================================
def run_simulation(broker: str, port: int, scenario: str, duration: int, interval: float):
    client_id = f"flood-simulator-{random.randint(1000, 9999)}"
    client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    logger.info(f"Connecting to MQTT broker {broker}:{port}...")
    try:
        client.connect(broker, port, keepalive=60)
        client.loop_start()
    except Exception as e:
        logger.error(f"Could not connect to MQTT broker at {broker}:{port}: {e}")
        return

    start_time = time.time()
    logger.info(f"Starting simulation scenario: [{scenario.upper()}] for {duration} seconds...")

    try:
        while True:
            elapsed = time.time() - start_time
            if duration > 0 and elapsed >= duration:
                logger.info(f"Simulation completed ({duration}s reached).")
                break

            current_ts = int(time.time())

            for node in NODES:
                # Calculate dynamic depth and rain according to scenario
                ratio = node.depth_cm / node.capacity_cm

                if scenario == "normal":
                    node.rain_mm_h = max(0.0, round(random.gauss(5.0, 2.0), 1))
                    target_depth = node.capacity_cm * 0.25 + random.uniform(-2, 2)
                    node.depth_cm += (target_depth - node.depth_cm) * 0.1

                elif scenario == "watch":
                    node.rain_mm_h = max(15.0, round(random.gauss(25.0, 5.0), 1))
                    target_depth = node.capacity_cm * 0.60 + random.uniform(-3, 3)
                    node.depth_cm += (target_depth - node.depth_cm) * 0.15

                elif scenario == "critical":
                    node.rain_mm_h = max(40.0, round(random.gauss(65.0, 8.0), 1))
                    target_depth = node.capacity_cm * 0.90 + random.uniform(-1, 2)
                    node.depth_cm += (target_depth - node.depth_cm) * 0.2

                elif scenario == "storm":
                    # Scripted 75-second multi-phase cloudburst
                    # 0-15s: Dry baseline
                    # 15-35s: Heavy cloudburst onset, rain 55 mm/h, surge to WATCH/WARNING
                    # 35-55s: Peak inundation reaching CRITICAL (>85%), gates auto-close
                    # 55-75s: Subsiding rain, floodgate holds back backflow, drainage begins
                    if elapsed < 15:
                        phase = "Phase 1: Dry Baseline"
                        node.rain_mm_h = max(0.0, round(random.uniform(2.0, 8.0), 1))
                        node.depth_cm = node.capacity_cm * 0.25 + random.uniform(-1.0, 1.0)
                    elif elapsed < 35:
                        phase = "Phase 2: Cloudburst Onset"
                        progress = (elapsed - 15) / 20.0
                        node.rain_mm_h = round(15.0 + progress * 45.0 + random.uniform(-3, 3), 1)
                        # Water rising rapidly
                        target = node.capacity_cm * (0.30 + progress * 0.48) # rises to ~78%
                        node.depth_cm = round(target + random.uniform(-1.5, 1.5), 1)
                    elif elapsed < 55:
                        phase = "Phase 3: Peak Inundation (CRITICAL)"
                        node.rain_mm_h = max(45.0, round(random.gauss(60.0, 5.0), 1))
                        # Surges past 85% into critical
                        target = node.capacity_cm * (0.86 + random.uniform(0.01, 0.08))
                        node.depth_cm = round(min(node.capacity_cm, target), 1)
                    else:
                        phase = "Phase 4: Subsiding & Drainage"
                        node.rain_mm_h = max(5.0, round(15.0 - (elapsed - 55) * 0.5, 1))
                        node.depth_cm = round(max(node.capacity_cm * 0.45, node.depth_cm - 1.2), 1)

                    if node.id == "drain-01" and int(elapsed) % 10 == 0:
                        logger.info(f"⏳ Storm Scenario [{phase}] - Elapsed: {int(elapsed)}s")

                # Clamp depth and rain
                node.depth_cm = max(0.0, min(node.capacity_cm, round(node.depth_cm, 1)))
                node.rain_mm_h = max(0.0, round(node.rain_mm_h, 1))
                node.rssi = random.randint(-72, -58)

                # Determine cadence: 2s if depth > 70% of capacity, otherwise 10s (or interval arg)
                effective_interval = 2.0 if (node.depth_cm / node.capacity_cm) > 0.70 else interval
                if (time.time() - node.last_published) >= effective_interval:
                    node.last_published = time.time()
                    payload = {
                        "node": node.id,
                        "ts": current_ts,
                        "depth_cm": node.depth_cm,
                        "rain_mm_h": node.rain_mm_h,
                        "gate_deg": node.gate_deg,
                        "rssi": node.rssi,
                    }
                    topic_telem = f"flood/v1/{node.id}/telemetry"
                    client.publish(topic_telem, json.dumps(payload))

                    risk_level = "CRITICAL" if ratio >= 0.85 else ("WARNING" if ratio >= 0.70 else ("WATCH" if ratio >= 0.50 else "NORMAL"))
                    color = "\033[91m" if risk_level == "CRITICAL" else ("\033[93m" if risk_level in ["WARNING", "WATCH"] else "\033[92m")
                    reset = "\033[0m"
                    logger.info(
                        f"📡 [{node.id}] {color}{risk_level:<8}{reset} | Depth: {node.depth_cm:5.1f}/{node.capacity_cm:.0f}cm ({ratio*100:4.1f}%) | "
                        f"Rain: {node.rain_mm_h:4.1f} mm/h | Gate: {node.gate_deg:2d}° | Rate: {effective_interval:.0f}s"
                    )

            time.sleep(1.0)

    except KeyboardInterrupt:
        logger.info("Simulation interrupted by operator.")
    finally:
        for node in NODES:
            client.publish(f"flood/v1/{node.id}/status", "offline", qos=1, retain=True)
        client.loop_stop()
        client.disconnect()
        logger.info("Disconnected from MQTT broker.")

parser = argparse.ArgumentParser(description="flood-ews Multi-Node Telemetry Simulator")
parser.add_argument("--broker", default=os.getenv("MQTT_BROKER_HOST", "broker.hivemq.com"), help="MQTT broker host")
parser.add_argument("--port", type=int, default=int(os.getenv("MQTT_BROKER_PORT", 1883)), help="MQTT broker port")
parser.add_argument("--scenario", choices=["normal", "watch", "warning", "critical", "storm"], default="storm", help="Simulation scenario")
parser.add_argument("--duration", type=int, default=75, help="Simulation duration in seconds (0 for indefinite)")
parser.add_argument("--interval", type=float, default=10.0, help="Normal telemetry publish interval (seconds)")

if __name__ == "__main__":
    args = parser.parse_args()
    run_simulation(args.broker, args.port, args.scenario, args.duration, args.interval)
