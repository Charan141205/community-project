# System Architecture: flood-ews

`flood-ews` is designed with an asynchronous, edge-to-cloud urban early warning architecture. It provides high resilience against extreme weather events through localized failsafes, hysteresis-based predictive risk classification, and dynamic routing that avoids inundated roadways.

---

## 1. End-to-End Data Flow

```mermaid
flowchart TD
    subgraph Edge ["Edge Layer (Drain Sensors & Floodgates)"]
        Sensor["ESP32 Microcontroller\nHC-SR04 + Potentiometer ADC"]
        LocalAutonomy["Local Autonomy Controller\n(Triggers if depth > 85% & disconnected)"]
        Servo["Micro Servo (0° Open - 90° Closed)"]
        Buzzer["Alarm Buzzer Siren"]
    end

    subgraph Transport ["Message Transport Layer"]
        Broker["MQTT Broker (HiveMQ / Mosquitto)\nTopics: telemetry, status, cmd"]
    end

    subgraph Backend ["FastAPI Core Services"]
        Ingest["MQTT Ingestion Engine\n(Paho asyncio bridge)"]
        RiskTracker["Risk Evaluation Engine\n(Rise rate + 3-tick hysteresis)"]
        GateAutomation["Automated Gate Controller\n(Actuates on WARNING/CRITICAL)"]
        AlertDispatcher["Multilingual Notification Dispatcher\n(Telugu, Hindi, English | 15-min rate limit)"]
        EvacEngine["Dijkstra Evacuation Router\n(300m Flood Avoidance Penalty & Pruning)"]
        WSHub["WebSocket Live Streaming Hub\n(/ws/live)"]
    end

    subgraph Storage ["Persistent Storage"]
        Timescale["TimescaleDB (readings Hypertable)\n5-min Continuous Aggregate & 30-day Retention"]
        Postgres["PostgreSQL Tables\n(nodes, alerts, subscribers, shelters, audit_logs)"]
    end

    subgraph Frontend ["Next.js 14 Presentation Layer"]
        PublicView["/public: Community Early Warning Portal\nLeaflet GIS Map, Alert Registration, Route Finder"]
        OpsView["/ops: SCADA Command Center\nTelemetry Charts, Manual Gate Override, Alert Feed"]
    end

    Sensor -->|telemetry: depth, rain, gate_deg| Broker
    Sensor -->|status: online / LWT offline| Broker
    Broker --> Ingest

    Ingest --> RiskTracker
    RiskTracker --> GateAutomation
    GateAutomation -->|cmd: gate_angle 90°| Broker
    Broker --> Servo

    RiskTracker --> AlertDispatcher
    RiskTracker --> EvacEngine
    RiskTracker --> WSHub

    Ingest --> Timescale
    AlertDispatcher --> Postgres
    GateAutomation --> Postgres

    WSHub --> PublicView
    WSHub --> OpsView

    Sensor -.->|Disconnected Failsafe| LocalAutonomy
    LocalAutonomy -.-> Servo
    LocalAutonomy -.-> Buzzer
```

---

## 2. Key Architecture Components

### A. Edge Layer & Local Autonomy
- **5-Sample Median Filter**: Discards acoustic echoes and transient water surface ripples in storm channels.
- **Adaptive Cadence**: 10-second normal cadence accelerates to 2 seconds when water depth exceeds 70% of channel capacity.
- **Failover Autonomy**: When network infrastructure collapses during an extreme cloudburst, the ESP32 node enters autonomous mode: if water exceeds 85% capacity, it directly actuates the gate to 90° and pulses the siren buzzer. Cloud commands seamlessly resume priority once network connectivity is re-established.

### B. Risk Classification & Hysteresis Engine
- **Rise Rate Computation**: $\text{rate} = \frac{\text{depth}_{\text{now}} - \text{depth}_{3\text{min}}}{\Delta t}$ in cm/min.
- **Risk Thresholds**:
  - `NORMAL`: fill ratio $< 50\%$ and rate $\le 5$ cm/min.
  - `WATCH`: $50\% \le \text{ratio} < 70\%$ OR rate $> 5$ cm/min.
  - `WARNING`: $70\% \le \text{ratio} < 85\%$ OR ($\text{rain} > 30$ mm/h and rising).
  - `CRITICAL`: fill ratio $\ge 85\%$.
- **Asymmetric Hysteresis**: Escalates instantaneously upon reaching an elevated threshold; requires 3 consecutive lower readings before de-escalating to prevent actuator chattering caused by storm waves.

### C. Dynamic Evacuation Graph Routing
- Utilizes NetworkX to model urban road networks.
- Applies a **100x travel time penalty** to all road segments within 300 meters of any node at `WARNING`.
- Completely **prunes/removes** road segments within 300 meters of any node at `CRITICAL`.
- Computes Dijkstra shortest path to the nearest relief shelter that currently has available bed capacity.

### D. Multilingual Alerting Engine
- Enforces a 15-minute cooldown per node on level escalation.
- Dynamically formats localized text alerts in **Telugu**, **Hindi**, and **English**.
- Injects citizen evacuation links directly into warning and critical alerts.
