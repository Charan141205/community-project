"""
MQTT Telemetry Consumer & Actuation Service for flood-ews.
Listens to sensor telemetry, validates payloads, runs the risk engine,
triggers automated floodgate closures, and coordinates multilingual alerts.
"""

import asyncio
from datetime import datetime, timezone
import json
import logging
from typing import Dict, Optional
import paho.mqtt.client as mqtt

from backend.app.config import settings
from backend.app.db import db
from backend.app.risk import NodeRiskTracker, RiskLevel
from backend.app.schemas import TelemetryPayload
from backend.app.alerts import alert_manager
from backend.app.websocket_manager import ws_manager

logger = logging.getLogger("flood_mqtt")

# Risk trackers dictionary per node
node_trackers: Dict[str, NodeRiskTracker] = {}


def get_or_create_tracker(node_id: str, capacity_cm: float = 180.0) -> NodeRiskTracker:
    if node_id not in node_trackers:
        node_trackers[node_id] = NodeRiskTracker(node_id=node_id, capacity_cm=capacity_cm)
    return node_trackers[node_id]


class MQTTService:
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def start(self, loop: asyncio.AbstractEventLoop):
        """Start the background MQTT client on the provided asyncio loop."""
        self._loop = loop
        client_id = f"flood-backend-core-{id(self)}"
        self.client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        logger.info(f"Connecting to MQTT broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}...")
        try:
            self.client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=settings.MQTT_KEEPALIVE)
            self.client.loop_start()
        except Exception as e:
            logger.warning(f"Could not connect to MQTT broker ({e}). Telemetry can also be fed via simulator/API.")

    def stop(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
            logger.info("MQTT client stopped.")

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.is_connected = True
            logger.info("MQTT Client connected successfully.")
            client.subscribe(settings.MQTT_TOPIC_TELEMETRY)
            client.subscribe(settings.MQTT_TOPIC_STATUS)
            logger.info(f"Subscribed to {settings.MQTT_TOPIC_TELEMETRY} and {settings.MQTT_TOPIC_STATUS}")
        else:
            logger.error(f"MQTT connect failed with rc={rc}")

    def _on_disconnect(self, client, userdata, disconnect_flags, rc=None, properties=None):
        self.is_connected = False
        logger.warning(f"MQTT Client disconnected (rc={rc})")

    def _on_message(self, client, userdata, msg):
        """MQTT message dispatcher (runs in paho background thread)."""
        if not self._loop:
            return

        topic = msg.topic
        payload_bytes = msg.payload

        try:
            payload_str = payload_bytes.decode("utf-8")
        except UnicodeDecodeError:
            logger.warning(f"Received malformed non-UTF8 payload on {topic}")
            return

        # Schedule async processing in main asyncio event loop
        asyncio.run_coroutine_threadsafe(
            self.process_message(topic, payload_str),
            self._loop,
        )

    async def process_message(self, topic: str, payload_str: str):
        """Asynchronously process telemetry and status messages."""
        topic_parts = topic.split("/")

        # Handle Node Status: flood/v1/{node_id}/status
        if len(topic_parts) >= 4 and topic_parts[3] == "status":
            node_id = topic_parts[2]
            status = payload_str.strip().lower()
            await db.update_node_status(node_id, status)
            await ws_manager.broadcast({
                "type": "node_status",
                "data": {"node_id": node_id, "status": status, "timestamp": datetime.now(timezone.utc).isoformat()},
            })
            return

        # Handle Telemetry: flood/v1/{node_id}/telemetry
        if len(topic_parts) >= 4 and topic_parts[3] == "telemetry":
            node_id = topic_parts[2]
            try:
                raw_json = json.loads(payload_str)
                # Pydantic v2 validation
                telemetry = TelemetryPayload.model_validate(raw_json)
            except Exception as val_err:
                logger.warning(f"Rejected invalid telemetry from [{node_id}]: {val_err}")
                return

            await self.handle_telemetry(telemetry)

    async def handle_telemetry(self, telem: TelemetryPayload):
        """Process validated telemetry reading."""
        node_id = telem.node
        node_data = await db.get_node_by_id(node_id)
        capacity_cm = node_data.get("capacity_cm", 180.0) if node_data else 180.0
        ward = node_data.get("ward", "Amberpet") if node_data else "General"
        node_name = node_data.get("name", node_id) if node_data else node_id

        reading_dt = datetime.fromtimestamp(telem.ts, tz=timezone.utc)
        reading_record = {
            "time": reading_dt,
            "node_id": node_id,
            "depth_cm": telem.depth_cm,
            "rain_mm_h": telem.rain_mm_h,
            "gate_deg": telem.gate_deg,
            "rssi": telem.rssi,
        }
        await db.insert_reading(reading_record)
        await db.update_node_status(node_id, "online", gate_deg=telem.gate_deg)

        # Run Risk Assessment with Hysteresis
        tracker = get_or_create_tracker(node_id, capacity_cm)
        risk_level, ratio, rise_rate, did_escalate = tracker.update(
            timestamp=float(telem.ts),
            depth_cm=telem.depth_cm,
            rain_mm_h=telem.rain_mm_h,
        )

        # Broadcast live telemetry to WebSockets
        await ws_manager.broadcast({
            "type": "telemetry",
            "data": {
                "node_id": node_id,
                "name": node_name,
                "ward": ward,
                "time": reading_dt.isoformat(),
                "depth_cm": telem.depth_cm,
                "capacity_cm": capacity_cm,
                "ratio": round(ratio, 2),
                "rain_mm_h": telem.rain_mm_h,
                "gate_deg": telem.gate_deg,
                "rssi": telem.rssi,
                "rise_rate_cm_min": rise_rate,
                "risk_level": risk_level.label,
            },
        })

        # AUTOMATION: On reaching WARNING or CRITICAL, actuate floodgate to 90 deg (closed)
        if risk_level in [RiskLevel.WARNING, RiskLevel.CRITICAL] and telem.gate_deg < 90:
            reason = f"auto:{risk_level.label.lower()}"
            logger.warning(f"🚨 AUTOMATION TRIGGER: Closing floodgate on [{node_id}] due to {risk_level.label}")
            self.publish_command(node_id, gate_angle=90, reason=reason)
            await db.log_gate_action(node_id, 90, reason, f"automation:{risk_level.label.lower()}")
            await ws_manager.broadcast({
                "type": "gate_actuation",
                "data": {"node_id": node_id, "gate_deg": 90, "reason": reason, "triggered_by": "automation"},
            })

        # ALERTS: Trigger multilingual broadcast ONLY on risk level escalation and respect rate limits
        if did_escalate and risk_level >= RiskLevel.WATCH:
            if alert_manager.should_send_alert(node_id):
                alert_manager.record_alert_sent(node_id)
                subscribers = await db.get_subscribers_by_ward(ward)
                evac_link = f"{settings.PUBLIC_URL}/public?evac=true&node={node_id}"

                for sub in subscribers:
                    lang = sub.get("language", "en")
                    phone = sub.get("phone", "")
                    msg = alert_manager.format_message(
                        language=lang,
                        level=risk_level.label,
                        node_name=node_name,
                        ward=ward,
                        ratio=ratio,
                        rain_mm_h=telem.rain_mm_h,
                        evac_link=evac_link,
                    )
                    await alert_manager.provider.send_message(phone, msg, channel="sms")

                # Store single representative alert in alerts table
                summary_msg = alert_manager.format_message("en", risk_level.label, node_name, ward, ratio, telem.rain_mm_h, evac_link)
                alert_id = await db.insert_alert(
                    node_id=node_id,
                    level=risk_level.label,
                    message=summary_msg,
                    channel="sms",
                    recipients_count=len(subscribers),
                )
                await ws_manager.broadcast({
                    "type": "alert",
                    "data": {
                        "id": alert_id,
                        "node_id": node_id,
                        "level": risk_level.label,
                        "message": summary_msg,
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                        "recipients_count": len(subscribers),
                    },
                })

    def publish_command(self, node_id: str, gate_angle: int, reason: str = "operator:override") -> bool:
        """Publish actuation command to MQTT broker: flood/v1/{node_id}/cmd"""
        if not self.client or not self.is_connected:
            logger.warning(f"MQTT client not connected, cannot publish command to [{node_id}]")
            return False

        topic = settings.MQTT_TOPIC_CMD.format(node_id=node_id)
        cmd_payload = {"gate_angle": gate_angle, "reason": reason}
        res = self.client.publish(topic, json.dumps(cmd_payload), qos=1)
        logger.info(f"Published command to {topic}: {cmd_payload} (mid={res.mid})")
        return res.rc == mqtt.MQTT_ERR_SUCCESS


# Global MQTT Service Singleton
mqtt_service = MQTTService()
