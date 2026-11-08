"""
Nodes API Endpoints.
Provides node listings, historical readings, and operator gate actuation overrides.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from backend.app.config import settings
from backend.app.db import db
from backend.app.mqtt_service import get_or_create_tracker, mqtt_service
from backend.app.schemas import GateOverrideRequest, NodeResponse, ReadingResponse
from backend.app.websocket_manager import ws_manager

router = APIRouter(prefix="/api/nodes", tags=["nodes"])


def verify_operator_key(x_api_key: Optional[str] = Header(None)):
    """Simple API Key validation for operator control endpoints."""
    if not x_api_key or x_api_key != settings.OPERATOR_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header for operator control",
        )
    return True


@router.get("", response_model=List[NodeResponse])
async def list_nodes():
    """List all sensor nodes with latest readings and live computed risk levels."""
    nodes = await db.get_all_nodes()
    response = []

    for node in nodes:
        node_id = node["id"]
        readings = await db.get_node_readings(node_id, limit=1)
        latest_reading = readings[-1] if readings else None

        tracker = get_or_create_tracker(node_id, node.get("capacity_cm", 180.0))
        risk_level = tracker.current_level.label

        latest_depth = latest_reading["depth_cm"] if latest_reading else None
        latest_rain = latest_reading["rain_mm_h"] if latest_reading else None
        latest_ratio = round(latest_depth / node["capacity_cm"], 2) if latest_depth and node.get("capacity_cm") else None

        # Calculate latest rise rate from tracker history
        history_list = list(tracker.history)
        rise_rate = None
        if history_list and latest_depth is not None:
            rise_rate = round(history_list[-1][1] - history_list[0][1], 2) if len(history_list) > 1 else 0.0

        response.append(NodeResponse(
            id=node["id"],
            name=node["name"],
            lat=node["lat"],
            lon=node["lon"],
            ward=node["ward"],
            mount_height_cm=node["mount_height_cm"],
            capacity_cm=node["capacity_cm"],
            status=node.get("status", "offline"),
            last_seen=node.get("last_seen"),
            current_gate_deg=node.get("current_gate_deg", 0),
            latest_depth_cm=latest_depth,
            latest_rain_mm_h=latest_rain,
            latest_ratio=latest_ratio,
            rise_rate_cm_min=rise_rate,
            risk_level=risk_level,
        ))

    return response


@router.get("/{node_id}/readings", response_model=List[ReadingResponse])
async def get_node_readings(
    node_id: str,
    limit: int = Query(60, ge=1, le=500, description="Number of historical samples to return for sparklines"),
):
    """Retrieve historical telemetry readings for sparkline charting."""
    node = await db.get_node_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node [{node_id}] not found")

    readings = await db.get_node_readings(node_id, limit=limit)
    return [
        ReadingResponse(
            time=r["time"],
            node_id=r["node_id"],
            depth_cm=r["depth_cm"],
            rain_mm_h=r["rain_mm_h"],
            gate_deg=r.get("gate_deg", 0),
            rssi=r.get("rssi", -70),
        )
        for r in readings
    ]


@router.post("/{node_id}/gate")
async def override_gate(
    node_id: str,
    req: GateOverrideRequest,
    authorized: bool = Depends(verify_operator_key),
):
    """
    Operator Floodgate Override.
    Requires `X-API-Key` header matching `OPERATOR_API_KEY`.
    Publishes actuation command to MQTT broker and logs audit trail.
    """
    node = await db.get_node_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node [{node_id}] not found")

    reason = f"operator:{req.reason}"
    published = mqtt_service.publish_command(node_id, req.gate_angle, reason)
    await db.log_gate_action(node_id, req.gate_angle, reason, "operator:manual")

    await ws_manager.broadcast({
        "type": "gate_actuation",
        "data": {
            "node_id": node_id,
            "gate_deg": req.gate_angle,
            "reason": reason,
            "triggered_by": "operator",
        },
    })

    return {
        "status": "success",
        "node_id": node_id,
        "gate_angle": req.gate_angle,
        "reason": reason,
        "mqtt_dispatched": published,
    }
