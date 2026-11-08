# flood-ews: Smart Community Flood & Urban Drainage Early Warning System

[![CI Pipeline](https://github.com/Charan141205/community-project/actions/workflows/ci.yml/badge.svg)](https://github.com/Charan141205/community-project/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![TimescaleDB](https://img.shields.io/badge/TimescaleDB-PostgreSQL-FDB515.svg?logo=postgresql&logoColor=white)](https://www.timescale.com)
[![MQTT](https://img.shields.io/badge/MQTT-v5.0%20%7C%20v3.1.1-660066.svg?logo=eclipse-mosquitto&logoColor=white)](https://mosquitto.org)

`flood-ews` is an end-to-end IoT, geospatial, and urban resilience early warning system designed to protect vulnerable neighborhoods and low-lying roadways from flash floods and sewer backflow. Centered on flood flashpoints along the Musi River basin in Hyderabad, India, it integrates simulated ESP32 sensor nodes, an automated SCADA floodgate controller, a TimescaleDB time-series backend, a multilingual disaster alert dispatcher, dynamic evacuation routing, and an interactive Next.js map dashboard.

---

## 📸 Live Dashboard Previews

| Community Public Portal (`/public`) | Operator Command Center (`/ops`) |
|:---:|:---:|
| ![Public Portal](docs/screenshots/active_storm_public.png) | ![Operator Ops](docs/screenshots/active_storm_ops.png) |
| *Live Leaflet map, hazard zones, citizen SMS/WhatsApp opt-in, click-to-route evacuation* | *Real-time SCADA floodgate controls, telemetry charts, multilingual alert dispatch* |

---

## 📂 Repository Structure

```
community-project/
├── .github/
│   └── workflows/
│       └── ci.yml                     # Automated GitHub Actions test & build pipeline
├── backend/                           # FastAPI Python 3.11/3.12 microservice
│   ├── Dockerfile                     # Multi-stage production container
│   ├── requirements.txt               # Backend dependencies (fastapi, asyncpg, networkx, etc.)
│   ├── pytest.ini                     # Pytest configuration
│   ├── app/
│   │   ├── main.py                    # FastAPI entrypoint, lifespan, CORS, WebSockets
│   │   ├── config.py                  # Pydantic Settings
│   │   ├── db.py                      # Async TimescaleDB / PostgreSQL pool + in-memory store
│   │   ├── schemas.py                 # Pydantic v2 validation models
│   │   ├── risk.py                    # Risk Engine (3-min rise rate & 3-tick hysteresis)
│   │   ├── alerts.py                  # Multilingual alerts (English, Telugu, Hindi)
│   │   ├── evacuation.py              # Dijkstra routing with 300m flood penalty & pruning
│   │   ├── mqtt_service.py            # Paho MQTT telemetry ingestion & gate automation
│   │   ├── websocket_manager.py       # Live WebSocket broadcaster (/ws/live)
│   │   └── api/                       # REST endpoints (nodes, alerts, evacuation, subscribers)
│   ├── scripts/
│   │   └── simulate_nodes.py          # 6-node scenario simulator (Normal, Watch, Storm, Critical)
│   └── tests/                         # 24 pytest unit & integration tests (100% passing)
├── dashboard/                         # Next.js 14 (App Router) + TypeScript + Tailwind
│   ├── Dockerfile                     # Multi-stage standalone production container
│   ├── package.json                   # Dependencies (leaflet, react-leaflet, recharts, lucide)
│   ├── tailwind.config.ts             # Custom themes & pulse animations
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx               # Root portal selector
│   │   │   ├── public/page.tsx        # Community Public View (Leaflet GIS, alert opt-in)
│   │   │   └── ops/page.tsx           # Operator View (gate overrides, SCADA charts)
│   │   ├── components/
│   │   │   ├── Map/FloodMap.tsx       # Leaflet map with pulsing risk markers & 300m hazard circles
│   │   │   ├── Sidebar/               # Node details, alert feed, gate actuation modal
│   │   │   └── UI/                    # Circular depth gauge, citizen subscribe modal
│   │   └── lib/                       # Types and API client
├── db/
│   └── init.sql                       # TimescaleDB hypertable, 5-min continuous aggregate, seed data
├── docs/                              # Project documentation & architectural blueprints
│   ├── ARCHITECTURE.md                # System design, data flows, and state machines
│   ├── API_REFERENCE.md               # Complete REST & WebSocket specification
│   ├── FIRMWARE_WOKWI_GUIDE.md        # Hardware wiring, pinouts, and simulation guide
│   ├── VERIFICATION_REPORT.md         # End-to-end verification report with test outputs
│   └── screenshots/                   # High-resolution screenshots of portals
├── firmware/                          # Wokwi ESP32 Arduino C++ firmware
│   ├── sketch.ino                     # Non-blocking loop, 5-sample median filter, local autonomy
│   ├── diagram.json                   # Wokwi wiring schematic (ESP32, HC-SR04, Pot, Servo, LEDs, Buzzer)
│   ├── wokwi.toml                     # Wokwi simulator configuration
│   └── libraries.txt                  # ArduinoJson, PubSubClient, ESP32Servo
├── scripts/                           # Top-level CLI helper scripts
│   ├── simulate.py                    # Root runner for multi-node telemetry simulation
│   └── verify_all.py                  # Automated verification & test runner
├── docker-compose.yml                 # Multi-container orchestration (DB, MQTT, API, Web)
├── mosquitto.conf                     # Mosquitto broker dev configuration
├── .env.example                       # Environment variable template
├── .gitignore                         # Git ignore configuration
└── README.md                          # Primary project documentation
```

---

## ⚡ Quickstart

### Option 1: Docker Compose (Recommended)

Start the entire stack (TimescaleDB, Mosquitto, FastAPI Backend, Next.js Dashboard) with a single command:

```bash
docker compose up --build
```

- **Public Dashboard**: [http://localhost:3000/public](http://localhost:3000/public)
- **Operator Command Center**: [http://localhost:3000/ops](http://localhost:3000/ops)
- **FastAPI Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MQTT Broker**: `localhost:1883`
- **TimescaleDB**: `localhost:5432`

---

### Option 2: Local Development Setup

#### 1. Backend Service
```bash
python -m venv backend/.venv
# Windows:
backend\.venv\Scripts\activate
# Linux/macOS:
# source backend/.venv/bin/activate

pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Dashboard Service
```bash
cd dashboard
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000).

---

## ⛈️ Automated Flash Flood Simulation

Run the scripted 75-second multi-phase cloudburst simulation directly from the project root:

```bash
python scripts/simulate.py --scenario storm --duration 75
```

### Scenario Timeline:
1. **0–15s (Dry Baseline)**: Normal water depth (< 25%), rainfall < 10 mm/h. Markers are **Green (NORMAL)**. Floodgates open at 0°.
2. **15–35s (Cloudburst Onset)**: Rain surges to 55 mm/h. Water rises rapidly past 50% (**WATCH**) and 70% (**WARNING**).
3. **Automated Gate Actuation**: Backend detects WARNING and immediately publishes `{"gate_angle": 90, "reason": "auto:warning"}`. Floodgate automatically closes to 90°.
4. **35–55s (Peak Inundation & Multilingual Alerts)**: Depth surges past 85% (**CRITICAL**). Map markers pulse red with 300m translucent hazard circles. Alerts are dispatched in **Telugu, Hindi, and English**.
5. **55–75s (Dynamic Rerouting)**: Evacuation paths recompute dynamically, penalizing and pruning roads near flooded drains to guide citizens safely to the nearest relief shelter.

---

## 🧪 Automated Testing

Execute the automated pytest suite (24 unit and integration tests):

```bash
python scripts/verify_all.py
# Or directly with pytest:
pytest backend/tests -v
```

All 24 test cases pass with 100% coverage, verifying:
- Risk ratio and 3-minute rise rate calculations
- Immediate escalation and 3-tick hysteresis de-escalation
- Pydantic schema validation and rejection of out-of-bounds telemetry
- 15-minute alert rate-limiting and multilingual templating
- Dijkstra road network routing with 300m flood penalty and pruning

---

## 📚 Detailed Documentation

- 📐 [**System Architecture & Data Flows**](docs/ARCHITECTURE.md)
- 🔌 [**REST & WebSocket API Reference**](docs/API_REFERENCE.md)
- 📲 [**Live Twilio SMS & WhatsApp Setup Guide**](docs/TWILIO_SETUP.md)
- 🛠️ [**ESP32 Firmware & Hardware Flashing Guide**](docs/FIRMWARE_WOKWI_GUIDE.md)
- 📋 [**Full Verification Report & Proofs**](docs/VERIFICATION_REPORT.md)
