"""
Unit tests for Pydantic schema validation.
Ensures invalid telemetry, out-of-range gate angles, and malformed inputs are rejected.
"""

import pytest
from pydantic import ValidationError
from backend.app.schemas import (
    TelemetryPayload,
    GateCommand,
    GateOverrideRequest,
    SubscriberCreate,
)


def test_valid_telemetry_payload():
    data = {
        "node": "drain-07",
        "ts": 1731060000,
        "depth_cm": 42.5,
        "rain_mm_h": 18.2,
        "gate_deg": 0,
        "rssi": -61,
    }
    payload = TelemetryPayload.model_validate(data)
    assert payload.node == "drain-07"
    assert payload.depth_cm == 42.5
    assert payload.rain_mm_h == 18.2
    assert payload.gate_deg == 0
    assert payload.rssi == -61


def test_invalid_telemetry_negative_depth():
    data = {
        "node": "drain-01",
        "ts": 1731060000,
        "depth_cm": -5.0,  # Negative depth is physically impossible
        "rain_mm_h": 10.0,
    }
    with pytest.raises(ValidationError):
        TelemetryPayload.model_validate(data)


def test_invalid_telemetry_gate_angle():
    data = {
        "node": "drain-01",
        "ts": 1731060000,
        "depth_cm": 30.0,
        "rain_mm_h": 10.0,
        "gate_deg": 120,  # Exceeds max 90 degrees
    }
    with pytest.raises(ValidationError):
        TelemetryPayload.model_validate(data)


def test_gate_command_validation():
    valid = GateCommand(gate_angle=90, reason="auto:warning")
    assert valid.gate_angle == 90

    with pytest.raises(ValidationError):
        GateCommand(gate_angle=-10, reason="invalid")


def test_subscriber_phone_validation():
    valid = SubscriberCreate(
        phone="+91-9876543210",
        name="Lakshmi Devi",
        ward="Amberpet",
        language="te",
    )
    assert valid.phone == "+919876543210"

    with pytest.raises(ValidationError):
        SubscriberCreate(
            phone="123",  # Too short
            name="A",
            ward="B",
        )
