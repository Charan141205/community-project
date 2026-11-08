# report_data_ch3_ch4.py
"""
Chapter 3 (Analysis & Design) and Chapter 4 (Implementation) content
for the Mohan Babu University (MBU) TESP Project Report.
Exhaustive, rigorous academic prose formatted with proper spacing and separated lists.
"""

CH3_REQ_INTRO = (
    "Engineering an effective cyber-physical early warning system requires a comprehensive decomposition of functional and non-functional "
    "requirements across the edge embedded layer, communication backbone, cloud microservices, and user interfaces."
)

CH3_FR_INTRO = "Functional Requirements (FR):"
CH3_FR_ITEMS = [
    "FR1 (High-Frequency Hydrological Telemetry): The edge node must sample ultrasonic distance every 500 milliseconds, compute water depth and percentage fill against calibrated culvert capacity, and publish telemetry packets to the cloud broker every 3 seconds or immediately upon detecting a delta shift >= 5 cm.",
    "FR2 (Autonomous Edge Failsafe Actuation): The edge microcontroller must evaluate local fill thresholds in firmware: if fill percentage crosses 70%, the ESP32 must autonomously actuate the servo-driven floodgate to 90° (Closed), illuminate the red alarm LED, and sound the audible buzzer siren within 50 milliseconds, operating with zero reliance on cloud connectivity.",
    "FR3 (Bi-Directional Cloud Command & Control): The cloud backend and authorized operators must be capable of transmitting manual override actuation commands (e.g., forcing floodgates open or shut) via authenticated MQTT command topics.",
    "FR4 (Dynamic Risk Assessment & Hysteresis): The backend risk engine must analyze incoming telemetry, evaluate the rate of water rise (cm/min), integrate predictive weather forecasts, and enforce a 3-tick hysteresis cooldown before de-escalating risk states to eliminate false alarm chatter.",
    "FR5 (Flood-Aware Dijkstra Evacuation Routing): The routing service must model the urban road network as a graph, calculate real-time edge penalty weights based on drain node risk levels, and compute optimal obstacle-avoiding evacuation paths to safe relief shelters.",
    "FR6 (Multilingual Citizen Alerting): Upon risk escalation, the system must query registered ward subscribers and dispatch localized warnings in Telugu, Hindi, or English via SMS and WhatsApp gateways with embedded dynamic evacuation navigation links.",
]

CH3_NFR_INTRO = "Non-Functional Requirements (NFR):"
CH3_NFR_ITEMS = [
    "NFR1 (Actuation Latency): Edge failsafe actuation must execute in under 50 milliseconds locally; cloud-commanded overrides must complete in under 500 milliseconds under standard broadband conditions.",
    "NFR2 (System Reliability & Availability): Ingestion pipelines and database services must maintain 99.9% uptime, gracefully reconnecting to MQTT brokers upon transient socket drops.",
    "NFR3 (Data Persistence & Scalability): TimescaleDB hypertables must support ingestion rates exceeding 1,000 samples/second with automated 30-day retention policies and 5-minute continuous aggregate pre-computations.",
    "NFR4 (Anti-Spam Rate Limiting): Citizen alerting pipelines must enforce a strict 15-minute cooldown per drainage flashpoint to prevent telecom message spamming and citizen panic.",
]

CH3_ARCH_INTRO = "The flood-ews platform is organized into five tightly coupled architectural layers:"
CH3_ARCH_LAYERS = [
    "1. Perception & Sensing Layer: Deployed at culvert flashpoints, comprising ultrasonic distance transducers and environmental precipitation monitors.",
    "2. Edge Computing Layer: ESP32 dual-core microcontrollers executing an autonomous Finite State Machine (FSM) that governs local sensing, noise filtering, LED/buzzer alarms, and PWM servo gate actuation.",
    "3. Transport & Broker Layer: Lightweight MQTT QoS 1 publish-subscribe broker (Eclipse Mosquitto / HiveMQ Cloud) handling secure, topic-isolated telemetry streaming and command routing.",
    "4. Cloud Microservices Layer: Containerized Python FastAPI application executing asynchronous workers for telemetry ingestion, risk evaluation, predictive weather polling, TimescaleDB persistence, and Dijkstra graph path computation.",
    "5. Presentation & Notification Layer: Modern Next.js React web portals (an Operator SCADA Command Center and a Public Citizen Portal) coupled with carrier-grade SMS and WhatsApp notification gateways.",
]

CH3_HARDWARE = [
    (
        "The physical sensing node is powered by the Espressif ESP32-WROOM-32 DevKit V1 microcontroller, selected for its high clock speed "
        "(240 MHz dual-core Tensilica Xtensa LX6), integrated 802.11 b/g/n Wi-Fi, low power consumption during sleep modes, and extensive GPIO "
        "peripherals supporting hardware Pulse Width Modulation (PWM) and hardware timers."
    ),
    (
        "Distance sensing is performed using the HC-SR04 ultrasonic transducer module. The module emits an eight-cycle 40 kHz acoustic burst when "
        "triggered by a 10 microsecond high pulse on its TRIG pin. The ECHO pin remains high for the duration of the acoustic wave's round trip, "
        "allowing the ESP32 to measure pulse duration using high-precision microsecond timers. The water surface distance d is derived as:\n\n"
        "d = (t_echo * 0.0343) / 2  (cm)"
    ),
    (
        "Floodgate actuation is achieved using a high-torque MG995 / SG90 servo motor mechanically coupled to an acrylic sluice gate. The ESP32 "
        "modulates the servo position using a 50 Hz PWM carrier signal with pulse widths ranging from 500 microseconds (representing 0°, "
        "Gate Fully Open) to 2500 microseconds (representing 90°, Gate Fully Closed). Local audiovisual warnings are provided by high-intensity "
        "diffused LEDs (Green for Normal, Red for Warning/Critical) and a resonant active piezoelectric buzzer operating at 2.4 kHz (85 dB SPL)."
    ),
    (
        "To ensure robust signal integrity and prevent GPIO strapping pin conflicts during ESP32 bootup, peripherals are mapped to dedicated "
        "non-conflicting pins. Table 3.1 details the hardware GPIO mapping utilized in both physical boards and the Wokwi simulation environment. "
        "Figure 3.1 illustrates the complete circuit schematic with color-coded interconnects and decoupling power rails."
    ),
]

TABLE_3_1_DATA = [
    ["TRIG", "GPIO 5", "Output", "Ultrasonic Transducer Trigger (10 µs pulse)", "Blue wire"],
    ["ECHO", "GPIO 18", "Input", "Ultrasonic Transducer Echo Pulse Input", "Yellow wire"],
    ["SERVO_PWM", "GPIO 19", "Output (PWM)", "Hardware LEDC PWM Servo Gate Signal (50 Hz)", "Orange wire"],
    ["LED_RED", "GPIO 21", "Output", "Warning / Critical Flood Alarm LED", "Purple wire"],
    ["LED_GREEN", "GPIO 22", "Output", "Normal Safe State Indicator LED", "Green wire"],
    ["BUZZER", "GPIO 23", "Output", "Active Audio Siren Alarm Transducer", "Brown wire"],
    ["VCC / VIN", "VIN (5V)", "Power", "Primary 5V Power Rail from USB / LDO Regulator", "Red wire"],
    ["GND", "GND", "Ground", "Common System Ground Plane", "Black wire"],
]

CH3_FSM_INTRO = (
    "The firmware is structured around a non-blocking, interrupt-driven Finite State Machine (FSM) executed within the main execution loop. "
    "Figure 3.2 depicts the formal state transition graph, comprising four operational states: STATE_NORMAL, STATE_WATCH, STATE_WARNING, "
    "and STATE_CRITICAL, supplemented by an autonomous LOCAL_FAILSAFE mode."
)

CH3_FSM_LOGIC_INTRO = "State Transition Logic:"
CH3_FSM_LOGIC_ITEMS = [
    "STATE_NORMAL (Fill < 50%): Green LED illuminated, Red LED off, Buzzer silent, Servo angle at 0° (Fully Open).",
    "STATE_WATCH (50% <= Fill < 70%): Telemetry reporting interval accelerates to 2 seconds to capture rapid hydrological changes.",
    "STATE_WARNING / CRITICAL (Fill >= 70%): Local autonomy immediately activates: Green LED off, Red LED on, Buzzer sirens, Servo angle rotates to 90° (Gate Closed). The node immediately publishes an emergency telemetry burst.",
    "LOCAL_FAILSAFE: If the ESP32 experiences continuous Wi-Fi or MQTT broker disconnects exceeding 10 seconds, it enters autonomous failsafe mode. In this mode, the edge node continues local sensor polling and threshold actuation uninterrupted, storing un-acknowledged telemetry in an internal circular buffer for burst transmission upon link restoration.",
]

CH3_BACKEND_INTRO = (
    "The cloud backend is engineered using Python 3.11 and the FastAPI asynchronous framework, deployed within a Docker container environment. "
    "The backend orchestrates four concurrent asynchronous tasks:"
)
CH3_BACKEND_TASKS = [
    "1. MQTT Ingestion Worker: Subscribes to flood/v1/+/telemetry and flood/v1/+/status using the Paho-MQTT client running on a dedicated background asyncio thread. Inbound JSON payloads are validated against Pydantic schema models before database insertion.",
    "2. Risk Evaluation Engine: Evaluates rate of rise, compares water levels against dynamic thresholds, and determines whether an escalation event has occurred.",
    "3. Predictive Weather Poller: Background worker querying Open-Meteo and IMD weather APIs every 30 minutes. If heavy rain (> 40 mm/h) is forecasted over Tirumala hills within the next hour, drain nodes in the foothill path are pre-emptively elevated to WATCH.",
    "4. WebSocket Real-Time Broadcaster: Manages active client browser connections on /ws/live, broadcasting instantaneous telemetry updates, gate actuation events, and emergency alerts to connected SCADA and citizen web clients.",
]

CH3_TIMESCALEDB = (
    "Persistent storage is managed by PostgreSQL 16 equipped with the TimescaleDB 2.14 extension. The core telemetry table 'readings' is "
    "converted into a TimescaleDB hypertable partitioned along the time dimension into 1-day chunks. Table 3.3 outlines the relational "
    "and time-series database tables, primary keys, and foreign key constraints."
)

TABLE_3_3_DATA = [
    ["nodes", "id (VARCHAR 32, PK)", "Drain node static metadata: name, lat, lon, ward, mount_height_cm, capacity_cm, status, current_gate_deg."],
    ["readings", "time (TIMESTAMPTZ), node_id (FK)", "Hypertable: depth_cm, rain_mm_h, gate_deg, rssi. Partitioned daily with 30-day retention."],
    ["readings_5min", "bucket (TIMESTAMPTZ), node_id", "Continuous Aggregate Materialized View: avg_depth, min_depth, max_depth, sample_count."],
    ["shelters", "id (VARCHAR 32, PK)", "Relief shelter metadata: name, lat, lon, capacity, current_occupancy, ward, contact_phone."],
    ["subscribers", "id (SERIAL, PK), phone (UNIQUE)", "Citizen alert registry: phone, name, ward, language ('te', 'hi', 'en'), opted_in."],
    ["alerts", "id (SERIAL, PK), node_id (FK)", "Historical alert audit log: level, message, channel, sent_at, recipients_count."],
    ["gate_audit_logs", "id (SERIAL, PK), node_id (FK)", "Actuation audit trail: gate_angle, reason, triggered_by ('automation' / 'operator')."],
]

CH3_RISK_FORMULATION = [
    (
        "The risk assessment engine evaluates incoming hydrological readings through a rigorous mathematical model combining absolute capacity "
        "fill ratios, instantaneous rate of rise, and hysteresis state memory."
    ),
    (
        "1. Instantaneous Water Depth and Fill Ratio:\n"
        "D_t = H_mount - d_measured\n"
        "R_t = D_t / C_drain\n\n"
        "where H_mount is sensor mount height (cm), d_measured is measured surface distance (cm), and C_drain is "
        "the calibrated flood capacity depth (cm)."
    ),
    (
        "2. Rate of Water Rise (v_rise):\n"
        "To detect flash flood surges before capacity thresholds are breached, the engine tracks a rolling window of readings over time interval delta_t:\n"
        "v_rise = (D_t - D_{t - delta_t}) / delta_t  (cm/min)\n\n"
        "If v_rise >= 10.0 cm/min or R_t >= 0.85, the node is classified as CRITICAL.\n"
        "If v_rise >= 5.0 cm/min or R_t >= 0.70, the node is classified as WARNING.\n"
        "If R_t >= 0.50 or incoming rain > 30 mm/h, the node is classified as WATCH. Otherwise, it remains NORMAL."
    ),
]

CH3_HYSTERESIS_INTRO = "3. Hysteresis Anti-Oscillation Algorithm:\nSurface water in turbulent storm canals exhibits severe wave oscillation, which can cause water levels to bounce rapidly across the 70% threshold. To eliminate false alarm chatter:"
CH3_HYSTERESIS_RULES = [
    "Escalation is instantaneous: If a reading breaches a higher threshold, the risk level escalates immediately.",
    "De-escalation requires 3 consecutive ticks: If a reading drops below a threshold, the system increments a de-escalation counter (k). Only when k >= 3 consecutive safe readings are observed does the risk level step down. Any transient spike immediately resets k = 0.",
]

CH3_DIJKSTRA = [
    (
        "During severe inundation, fleeing citizens must be directed along paths that actively circumvent flooded culverts and underpasses. "
        "The municipal road network is formalized as a directed graph G = (V, E), where V consists of road intersections, drainage nodes, and "
        "shelters, and E represents traversable roadway segments."
    ),
    (
        "Each edge (u, v) in E possesses a base physical distance d(u, v) computed via the Haversine spherical geodesic formula based on latitude "
        "and longitude coordinates. To incorporate live flood telemetry, the dynamic edge weight W(u, v) is calculated as:\n\n"
        "W(u, v) = d(u, v) * [1.0 + Sum_{n in {u, v}} P(n)]\n\n"
        "where the risk penalty function P(n) is defined as:\n"
        "• P(n) = 0.0 if Level(n) is NORMAL or WATCH\n"
        "• P(n) = 5.0 if Level(n) is WARNING\n"
        "• P(n) = 100.0 if Level(n) is CRITICAL\n\n"
        "Dijkstra's algorithm executes over graph G, computing the minimum-cost tree from the evacuee's origin to all registered shelters and "
        "selecting the shelter that minimizes total path weight while maintaining available shelter capacity."
    ),
]

TABLE_3_4_DATA = [
    ["drain-01", "Kapilatheertham Nallah", "13.6508° N", "79.4215° E", "shelter-01 (SV High School)", "1.45 km (Normal) / 4.80 km (Flooded)"],
    ["drain-02", "Leela Mahal Culvert", "13.6370° N", "79.4285° E", "shelter-03 (Municipal High School)", "0.85 km (Normal) / 2.90 km (Flooded)"],
    ["drain-03", "Railway Underbridge (West)", "13.6255° N", "79.4205° E", "shelter-02 (Mahati Relief Centre)", "0.62 km (Normal) / 3.40 km (Flooded)"],
    ["drain-04", "Korlagunta Storm Canal", "13.6330° N", "79.4350° E", "shelter-03 (Municipal High School)", "0.78 km (Normal) / 2.65 km (Flooded)"],
    ["drain-05", "Alipiri Footpath Channel", "13.6450° N", "79.4070° E", "shelter-01 (SV High School)", "0.92 km (Normal) / 3.10 km (Flooded)"],
    ["drain-06", "Tiruchanur Swarnamukhi Causeway", "13.6095° N", "79.4505° E", "shelter-02 (Mahati Relief Centre)", "3.80 km (Normal) / 8.20 km (Flooded)"],
]

CH4_SECTIONS = [
    (
        "4.1 Physical ESP32 Hardware Integration & Wokwi Simulation Setup",
        [
            (
                "To enable rigorous verification and academic demonstration, the embedded subsystem is implemented with dual deployment support: "
                "physical ESP32 hardware flashing and cloud-based Wokwi embedded simulation. In Wokwi, the exact circuit layout is specified via "
                "diagram.json, interconnecting the ESP32 DevKit V1 with an HC-SR04 ultrasonic sensor, SG90 servo motor, status LEDs, and buzzer."
            ),
            (
                "Figure 4.1 depicts the Wokwi simulation interface, showcasing breadboard wiring, pin connections, and the interactive distance slider "
                "that allows operators to simulate rising floodwaters from 2 cm up to 400 cm in real time."
            ),
        ]
    ),
    (
        "4.2 Firmware Implementation in C++ (PlatformIO) and MicroPython",
        [
            (
                "The firmware is developed in two distinct, production-tested paradigms:\n\n"
                "1. C++ Arduino Framework (PlatformIO): Utilizes non-blocking FreeRTOS hardware timers, native ESP32 ledcAttach() and ledcWrite() "
                "hardware PWM for jitter-free servo actuation, and the PubSubClient library for MQTT QoS 1 telemetry streaming.\n\n"
                "2. MicroPython Framework: Optimized for lightweight rapid deployment in modern virtual labs. Implemented in main.py, the MicroPython "
                "engine employs machine.PWM for servo horn positioning and raw byte string encoding (b'flood/v1/...') for strict compliance with the "
                "umqtt.simple protocol."
            ),
        ]
    ),
    (
        "4.3 MQTT Message Broker Setup & Topic Hierarchy",
        [
            (
                "Telemetry and command streaming utilize the public HiveMQ cloud broker (broker.hivemq.com:1883) during development and Eclipse Mosquitto "
                "with TLS 8883 for hardened production deployments. The topic architecture is strictly namespaced under flood/v1/{node_id}/:\n"
                "• Telemetry Topic: flood/v1/{node_id}/telemetry — Published by the ESP32 with QoS 1, carrying depth, rainfall, gate angle, and RSSI.\n"
                "• Command Topic: flood/v1/{node_id}/cmd — Subscribed by the ESP32 to receive remote operator gate override commands.\n"
                "• Status Topic: flood/v1/{node_id}/status — Published as an MQTT Retained message ('online' / 'offline') with Last Will and Testament (LWT)."
            ),
        ]
    ),
    (
        "4.4 FastAPI Asynchronous Backend Services",
        [
            (
                "The cloud backend service is implemented in backend/app/main.py. The service initializes an asynchronous lifespan context that manages "
                "the database connection pool (asyncpg), starts the background MQTT ingestion listener, and schedules periodic weather polling. "
                "Endpoints are modularized into dedicated routers:\n"
                "• /api/nodes: Exposes hydrological telemetry, current risk states, and gate actuation endpoints.\n"
                "• /api/evacuation: Computes dynamic Dijkstra evacuation paths given citizen origin coordinates and node IDs.\n"
                "• /api/alerts: Retrieves audit history of dispatched emergency notifications.\n"
                "• /api/subscribers: Provides public registration for citizens to opt in to SMS and WhatsApp warnings.\n"
                "• /ws/live: Full-duplex WebSocket channel streaming live telemetry deltas to active browser sessions."
            ),
        ]
    ),
    (
        "4.5 TimescaleDB Initialization, Continuous Aggregates & Audit Logging",
        [
            (
                "The database is provisioned via db/init.sql. The readings table is converted to a hypertable partitioned into daily chunks. A continuous "
                "materialized view readings_5min is scheduled with an automated refresh policy to compute rolling 5-minute averages, minimums, maximums, "
                "and sample counts. Furthermore, a 30-day retention policy (add_retention_policy) automatically purges aged telemetry chunks, ensuring "
                "the database footprint remains bounded on embedded edge servers."
            ),
        ]
    ),
    (
        "4.6 Next.js Operator SCADA Operations Portal",
        [
            (
                "The operator portal (http://localhost:3000/ops) is built using Next.js 14, Tailwind CSS, and React-Leaflet. It provides municipal "
                "operators with a dark-mode SCADA command center displaying:\n"
                "• Full-Screen Geospatial Map: Real-time status pins for all 6 Tirupati drainage nodes (pulsing green for Normal, yellow for Warning, red for Critical).\n"
                "• Live Telemetry Drawer: Real-time depth readings, fill percentages, and 6-hour historical trend sparklines.\n"
                "• Emergency Gate Actuation Controls: One-click manual override buttons allowing operators to actuate gates (0° Open, 90° Closed).\n\n"
                "Figure 4.2 presents the complete Operator SCADA Operations Command Center interface."
            ),
        ]
    ),
    (
        "4.7 Public Citizen Evacuation Portal & Interactive Routing Map",
        [
            (
                "The public citizen portal (http://localhost:3000/public) is optimized for mobile smartphones, enabling evacuating citizens to assess "
                "localized flood risks without logging in. When accessed via an emergency WhatsApp link, the portal automatically extracts the affected "
                "node ID, queries the backend Dijkstra service, and renders the safe turn-by-turn evacuation path directly onto an interactive OpenStreetMap "
                "view, clearly highlighting the destination shelter, route distance, and shelter contact numbers. Figure 4.3 illustrates the Public "
                "Citizen Portal interface."
            ),
        ]
    ),
    (
        "4.8 Automated Multi-Node Flash Flood Simulation Script",
        [
            (
                "To facilitate comprehensive stress testing and demonstration without requiring 6 physical ESP32 boards, a multi-threaded simulation tool "
                "backend/scripts/simulate_nodes.py was developed. The script models all 6 Tirupati nodes under various scenarios ('storm', 'normal', "
                "'watch', 'critical'). Crucially, the script features a --skip drain-01 flag that allows the user's live Wokwi ESP32 to drive drain-01 "
                "(Kapilatheertham Nallah) while the script simulates realistic monsoon hydrology across the remaining 5 drainage flashpoints."
            ),
        ]
    ),
]

TABLE_4_2_DATA = [
    ["Telugu (te)", "🚨 వరద హెచ్చరిక [CRITICAL]: {ward} లోని {node_name} వద్ద నీటిమట్టం {ratio}% చేరింది (వర్షం: {rain} mm/h). సురక్షిత తరలింపు మార్గం: {evac_link}"],
    ["Hindi (hi)", "🚨 बाढ़ चेतावनी [CRITICAL]: {ward} में {node_name} का जलस्तर {ratio}% तक पहुंच गया है (वर्षा: {rain} mm/h). सुरक्षित राहत शिविर मार्ग: {evac_link}"],
    ["English (en)", "🚨 FLOOD WARNING [CRITICAL]: {node_name} in {ward} is at {ratio}% capacity (Rain: {rain} mm/h). Evacuate via safe route: {evac_link}"],
]
