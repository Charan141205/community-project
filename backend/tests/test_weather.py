"""
Unit and integration tests for Predictive Weather Integration & Live Alert Dispatchers.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.risk import RiskLevel, evaluate_raw_risk, NodeRiskTracker
from backend.app.alerts import TwilioProvider, MockProvider, AlertManager


def test_predictive_weather_risk_elevation():
    """Verify that a forecasted heavy storm (>= 40 mm/h) pre-emptively triggers WATCH state."""
    # Under dry baseline (ratio 25%, current rain 5 mm/h, rise rate 0)
    # Without forecast -> NORMAL
    raw_level_normal = evaluate_raw_risk(
        ratio=0.25, rate_cm_min=0.0, rain_mm_h=5.0, forecast_rain_1h_mm_h=0.0
    )
    assert raw_level_normal == RiskLevel.NORMAL

    # With heavy storm forecast (45 mm/h) -> Pre-emptively elevates to WATCH!
    raw_level_watch = evaluate_raw_risk(
        ratio=0.25, rate_cm_min=0.0, rain_mm_h=5.0, forecast_rain_1h_mm_h=45.0
    )
    assert raw_level_watch == RiskLevel.WATCH

    # Severe cloudburst forecast (70 mm/h) + moderate depth (ratio 42%) -> Elevates to WARNING!
    raw_level_warning = evaluate_raw_risk(
        ratio=0.42, rate_cm_min=1.0, rain_mm_h=15.0, forecast_rain_1h_mm_h=70.0
    )
    assert raw_level_warning == RiskLevel.WARNING


def test_predictive_weather_with_node_tracker():
    """Verify NodeRiskTracker applies immediate escalation upon predictive forecast."""
    tracker = NodeRiskTracker(node_id="drain-01", capacity_cm=180.0)
    assert tracker.current_level == RiskLevel.NORMAL

    # Forecasted storm arrives in API data
    level, ratio, rate, did_escalate = tracker.update(
        timestamp=100.0,
        depth_cm=45.0,  # 25% capacity
        rain_mm_h=5.0,
        forecast_rain_1h_mm_h=48.0,
    )
    assert level == RiskLevel.WATCH
    assert did_escalate is True


@pytest.mark.asyncio
async def test_weather_forecast_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/weather/forecast")
        assert resp.status_code == 200
        data = resp.json()
        assert "source" in data
        assert "current_precipitation_mm_h" in data
        assert "storm_inbound" in data


@pytest.mark.asyncio
async def test_twilio_provider_unconfigured():
    """Verify TwilioProvider safely logs warning and returns False without credentials."""
    provider = TwilioProvider(account_sid="", auth_token="", from_sms_phone="")
    success = await provider.send_message("+919876543210", "Test alert", channel="sms")
    assert success is False
