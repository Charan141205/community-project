"""
Pydantic v2 schemas for request validation and API responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# TELEMETRY & MQTT SCHEMAS
# ============================================================================
class TelemetryPayload(BaseModel):
    """Raw telemetry payload sent by ESP32 sensor nodes."""
    node: str = Field(..., description="Unique node identifier, e.g. drain-01")
    ts: int = Field(..., description="Unix epoch timestamp in seconds")
    depth_cm: float = Field(..., ge=0.0, description="Measured water depth in centimeters")
    rain_mm_h: float = Field(..., ge=0.0, description="Simulated or measured precipitation rate in mm/h")
    gate_deg: int = Field(0, ge=0, le=90, description="Floodgate angle: 0 (Open) to 90 (Closed)")
    rssi: int = Field(-70, ge=-120, le=0, description="Wi-Fi signal strength in dBm")

    @field_validator("node")
    @classmethod
    def validate_node(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Node identifier cannot be empty")
        return v


class GateCommand(BaseModel):
    """Actuation command dispatched to ESP32 floodgate."""
    gate_angle: int = Field(..., ge=0, le=90, description="Target gate angle: 0 to 90 degrees")
    reason: str = Field("operator:manual", description="Reason for command actuation")


class GateOverrideRequest(BaseModel):
    """Operator gate override request."""
    gate_angle: int = Field(..., ge=0, le=90, description="Target gate angle")
    reason: str = Field("operator_manual_override", description="Reason for override")


# ============================================================================
# API MODELS & RESPONSES
# ============================================================================
RiskLevelStr = Literal["NORMAL", "WATCH", "WARNING", "CRITICAL"]


class ReadingResponse(BaseModel):
    time: datetime
    node_id: str
    depth_cm: float
    rain_mm_h: float
    gate_deg: int
    rssi: int


class NodeResponse(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    ward: str
    mount_height_cm: float
    capacity_cm: float
    status: str
    last_seen: Optional[datetime] = None
    current_gate_deg: int = 0
    latest_depth_cm: Optional[float] = None
    latest_rain_mm_h: Optional[float] = None
    latest_ratio: Optional[float] = None
    rise_rate_cm_min: Optional[float] = None
    risk_level: RiskLevelStr = "NORMAL"


class AlertResponse(BaseModel):
    id: int
    node_id: str
    level: str
    message: str
    channel: str
    sent_at: datetime
    recipients_count: int


class SubscriberCreate(BaseModel):
    phone: str = Field(..., description="Phone number with country code, e.g. +919876543210")
    name: str = Field(..., min_length=2, max_length=128)
    ward: str = Field(..., min_length=2, max_length=64)
    language: Literal["en", "te", "hi"] = Field("en", description="Preferred language")
    opted_in: bool = Field(True)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = "".join(c for c in v if c.isdigit() or c == "+")
        if len(clean) < 10:
            raise ValueError("Invalid phone number format")
        return clean


class SubscriberResponse(BaseModel):
    id: int
    phone: str
    name: str
    ward: str
    language: str
    opted_in: bool
    created_at: datetime


class ShelterResponse(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    capacity: int
    current_occupancy: int
    ward: str
    contact_phone: Optional[str] = None


class EvacuationRoute(BaseModel):
    shelter: ShelterResponse
    distance_km: float
    eta_minutes: float
    avoided_flooded_nodes: List[str]
    geojson: Dict[str, Any]  # GeoJSON Feature or LineString
