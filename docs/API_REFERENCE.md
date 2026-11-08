# REST & WebSocket API Reference: flood-ews

Base URL: `http://localhost:8000` (or configured via environment)  
Interactive OpenAPI Docs: `http://localhost:8000/docs`

---

## 1. REST Endpoints

### `GET /health`
Returns the operational health of backend services, database connection status, and MQTT broker state.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "flood-ews",
  "environment": "development",
  "timestamp": "2026-11-08T05:09:43.532329Z",
  "database": "connected",
  "mqtt_broker": "connected"
}
```

---

### `GET /api/nodes`
Lists all monitored drainage sensor nodes, including their latest telemetry, fill ratio, 3-minute rise rate, and live risk level.

**Response (200 OK):**
```json
[
  {
    "id": "drain-01",
    "name": "Moosarambagh Bridge",
    "lat": 17.3705,
    "lon": 78.508,
    "ward": "Amberpet",
    "mount_height_cm": 200.0,
    "capacity_cm": 180.0,
    "status": "online",
    "last_seen": "2026-11-08T05:12:03Z",
    "current_gate_deg": 90,
    "latest_depth_cm": 153.4,
    "latest_rain_mm_h": 54.8,
    "latest_ratio": 0.85,
    "rise_rate_cm_min": 6.8,
    "risk_level": "WARNING"
  }
]
```

---

### `GET /api/nodes/{id}/readings?limit=60`
Retrieves historical time-series samples for a given node to render Recharts sparklines.

**Query Parameters:**
- `limit` (optional, default: 60, min: 1, max: 500)

**Response (200 OK):**
```json
[
  {
    "time": "2026-11-08T05:10:00Z",
    "node_id": "drain-01",
    "depth_cm": 42.5,
    "rain_mm_h": 18.2,
    "gate_deg": 0,
    "rssi": -61
  }
]
```

---

### `POST /api/nodes/{id}/gate`
Operator override endpoint to manually actuate the floodgate (open: 0°, closed: 90°).

**Headers Required:**
- `X-API-Key: dev-operator-key-42`

**Request Body:**
```json
{
  "gate_angle": 90,
  "reason": "manual_emergency_closure"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "node_id": "drain-01",
  "gate_angle": 90,
  "reason": "operator:manual_emergency_closure",
  "mqtt_dispatched": true
}
```

---

### `GET /api/evacuation?lat={lat}&lon={lon}`
Computes the optimal safe evacuation route from coordinates to the nearest shelter, dynamically avoiding submerged roadways.

**Query Parameters:**
- `lat` (required): Citizen Latitude, e.g. `17.3710`
- `lon` (required): Citizen Longitude, e.g. `78.5085`

**Response (200 OK):**
```json
{
  "shelter": {
    "id": "shelter-02",
    "name": "Nimboliadda Community Hall",
    "lat": 17.382,
    "lon": 78.495,
    "capacity": 250,
    "current_occupancy": 15,
    "ward": "Malakpet",
    "contact_phone": "+91-40-24552233"
  },
  "distance_km": 2.28,
  "eta_minutes": 5.5,
  "avoided_flooded_nodes": ["drain-01", "drain-02"],
  "geojson": {
    "type": "Feature",
    "geometry": {
      "type": "LineString",
      "coordinates": [
        [78.5085, 17.371],
        [78.5095, 17.3712],
        [78.5, 17.3765],
        [78.495, 17.382]
      ]
    },
    "properties": {
      "distance_km": 2.28,
      "eta_minutes": 5.5,
      "target_shelter": "Nimboliadda Community Hall",
      "avoided_drains": ["drain-01", "drain-02"]
    }
  }
}
```

---

### `POST /api/subscribers`
Registers citizens for automated multilingual early warning alerts.

**Request Body:**
```json
{
  "phone": "+919876543210",
  "name": "Ramesh Kumar",
  "ward": "Amberpet",
  "language": "te",
  "opted_in": true
}
```

---

## 2. Real-Time WebSocket Hub: `/ws/live`

Connect via `ws://localhost:8000/ws/live` to receive broadcast events:

### Event Types:
1. **Telemetry Update**:
```json
{
  "type": "telemetry",
  "data": {
    "node_id": "drain-01",
    "name": "Moosarambagh Bridge",
    "depth_cm": 140.6,
    "capacity_cm": 180.0,
    "ratio": 0.78,
    "rain_mm_h": 73.4,
    "gate_deg": 90,
    "risk_level": "WARNING"
  }
}
```

2. **Alert Notification**:
```json
{
  "type": "alert",
  "data": {
    "id": 1,
    "node_id": "drain-01",
    "level": "WARNING",
    "message": "🚨 FLOOD ALERT [WARNING]: Water level in Moosarambagh Bridge has reached 78% capacity...",
    "sent_at": "2026-11-08T05:11:58Z"
  }
}
```

3. **Gate Actuation Event**:
```json
{
  "type": "gate_actuation",
  "data": {
    "node_id": "drain-01",
    "gate_deg": 90,
    "reason": "auto:warning",
    "triggered_by": "automation"
  }
}
```
