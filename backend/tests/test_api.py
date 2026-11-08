"""
Integration tests for FastAPI REST endpoints.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.config import settings


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "flood-ews"


@pytest.mark.asyncio
async def test_nodes_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/nodes")
        assert resp.status_code == 200
        nodes = resp.json()
        assert len(nodes) >= 6
        assert any(n["id"] == "drain-01" for n in nodes)


@pytest.mark.asyncio
async def test_subscribers_registration():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "phone": "+919988776655",
            "name": "Prasad Rao",
            "ward": "Alipiri",
            "language": "te",
            "opted_in": True,
        }
        resp = await client.post("/api/subscribers", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Prasad Rao"
        assert data["language"] == "te"


@pytest.mark.asyncio
async def test_evacuation_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/evacuation?lat=13.6500&lon=79.4210")
        assert resp.status_code == 200
        data = resp.json()
        assert "shelter" in data
        assert data["distance_km"] > 0
        assert data["geojson"]["type"] == "Feature"


@pytest.mark.asyncio
async def test_operator_gate_override_unauthorized():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/nodes/drain-01/gate", json={"gate_angle": 90, "reason": "emergency"})
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_operator_gate_override_authorized():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"X-API-Key": settings.OPERATOR_API_KEY}
        resp = await client.post(
            "/api/nodes/drain-01/gate",
            json={"gate_angle": 90, "reason": "manual_test"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["gate_angle"] == 90
