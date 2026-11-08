# report_data_frontmatter.py
"""
Front matter definitions for the Mohan Babu University (MBU) TESP Project Report.
Updated with clean title: SMART COMMUNITY FLOOD & URBAN DRAINAGE EARLY WARNING SYSTEM
"""

PROJECT_TITLE = "SMART COMMUNITY FLOOD & URBAN DRAINAGE EARLY WARNING SYSTEM"

ABSTRACT_TEXT = (
    "Urban flash flooding presents an escalating hazard to public safety and municipal infrastructure, particularly in foothill "
    "catchment cities such as Tirupati, India, where steep topography generates rapid surface runoff. This project presents the "
    "design, implementation, and empirical evaluation of 'flood-ews'—an autonomous Internet of Things (IoT) based Smart Community "
    "Flood and Urban Drainage Early Warning System. The architecture integrates edge-computing ESP32 telemetry nodes equipped with "
    "ultrasonic distance sensors and autonomous servo-actuated floodgate failsafes, communicating over a lightweight MQTT protocol "
    "with Quality of Service (QoS) Level 1. A centralized FastAPI asynchronous backend processes real-time telemetry, persists "
    "high-frequency time-series data in TimescaleDB hypertables, and evaluates multi-tier flood risks using a rate-of-rise and "
    "hysteresis engine to eliminate false alarms. To protect vulnerable communities, the system computes dynamic, flood-avoiding "
    "evacuation routes to designated relief shelters using Dijkstra's algorithm with adaptive edge penalties, dispatching localized "
    "alerts in Telugu, Hindi, and English via automated SMS and WhatsApp gateways. Experimental validation in both hardware and "
    "Wokwi simulation environments demonstrates edge failsafe actuation latency under 12 milliseconds, telemetry packet delivery "
    "exceeding 99.8%, and instantaneous evacuation route convergence across Tirupati's drainage network."
)

STUDENTS = [
    ("Lagisetty Vidya Charan", "23101A030061"),
    ("Kummara Nandakishore", "23101A030035"),
    ("Tajuddin Mohammad Ashraf", "23101A030001"),
    ("Shaik Sufiyan", "23101A030050"),
]

SUPERVISOR_NAME = "Dr. N. Gireesh, M.Tech, Ph.D."
SUPERVISOR_DESIG = "Professor, CoE"
SUPERVISOR_DEPT = "Department of ECE"

HOD_NAME = "Dr. N. Sudhakar Reddy, M.Tech, Ph.D."
HOD_DESIG = "Professor & Head"
HOD_DEPT = "Dept. of ECE"

ACRONYMS = [
    ("AI", "Artificial Intelligence"),
    ("API", "Application Programming Interface"),
    ("App-DDoS", "Application-Distributed Denial-of-Service"),
    ("BOM", "Bill of Materials"),
    ("CORS", "Cross-Origin Resource Sharing"),
    ("CPU", "Central Processing Unit"),
    ("DBMS", "Database Management System"),
    ("Dijkstra", "Dijkstra Shortest Path Graph Algorithm"),
    ("DMA", "Direct Memory Access"),
    ("ECE", "Electronics and Communication Engineering"),
    ("ESP32", "Espressif 32-bit Dual-Core Microcontroller with Wi-Fi & Bluetooth"),
    ("EWS", "Early Warning System"),
    ("FMEA", "Failure Mode and Effects Analysis"),
    ("FSM", "Finite State Machine"),
    ("GIS", "Geographic Information System"),
    ("GPIO", "General Purpose Input/Output"),
    ("GUI", "Graphical User Interface"),
    ("HC-SR04", "Ultrasonic Distance Transducer Module"),
    ("HTTP", "Hypertext Transfer Protocol"),
    ("HTTPS", "Hypertext Transfer Protocol Secure"),
    ("IDE", "Integrated Development Environment"),
    ("IEEE", "Institute of Electrical and Electronics Engineers"),
    ("IMD", "India Meteorological Department"),
    ("IoT", "Internet of Things"),
    ("JSON", "JavaScript Object Notation"),
    ("LED", "Light Emitting Diode"),
    ("MBU", "Mohan Babu University"),
    ("MQTT", "Message Queuing Telemetry Transport"),
    ("NIDS", "Network-based Intrusion Detection System"),
    ("PEO", "Program Educational Objective"),
    ("PO", "Program Outcome"),
    ("PSO", "Program Specific Outcome"),
    ("PWM", "Pulse Width Modulation"),
    ("QoS", "Quality of Service"),
    ("REST", "Representational State Transfer"),
    ("ROM", "Read Only Memory"),
    ("RSSI", "Received Signal Strength Indicator"),
    ("SCADA", "Supervisory Control and Data Acquisition"),
    ("SDK", "Software Development Kit"),
    ("SMS", "Short Message Service"),
    ("SPI", "Serial Peripheral Interface"),
    ("SSL/TLS", "Secure Sockets Layer / Transport Layer Security"),
    ("TCP/IP", "Transmission Control Protocol / Internet Protocol"),
    ("TESP", "Technology Extension for Societal Problems"),
    ("TOC", "Table of Contents"),
    ("UART", "Universal Asynchronous Receiver-Transmitter"),
    ("UI/UX", "User Interface / User Experience"),
    ("URL", "Uniform Resource Locator"),
    ("VS Code", "Visual Studio Code IDE"),
    ("WBS", "Work Breakdown Structure"),
    ("Wi-Fi", "Wireless Fidelity (IEEE 802.11 b/g/n)"),
    ("Wokwi", "Wokwi Embedded Systems Cloud Simulator"),
    ("WS", "WebSocket Bi-Directional Full-Duplex Protocol"),
]

FIGURES = [
    ("1.1", "Geographical Catchment Map of Seshachalam Foothills and Swarnamukhi Drainage Basin in Tirupati", "8"),
    ("1.2", "High-Level Conceptual Block Diagram of the flood-ews Early Warning System", "10"),
    ("2.1", "Architectural Evolution of Hydrological Telemetry from Manual Gauges to Autonomous Edge IoT", "14"),
    ("2.2", "Communication Protocol Latency and Overhead Comparison: MQTT Publish-Subscribe vs. HTTP Polling", "17"),
    ("3.1", "Complete Circuit Schematic and Pin Interconnections of the ESP32 Drainage Telemetry Node", "22"),
    ("3.2", "Finite State Machine (FSM) State Transition Diagram for Autonomous Edge Floodgate Control", "25"),
    ("3.3", "End-to-End System Microservices Architecture and Cloud Message Broker Topology", "28"),
    ("3.4", "Entity-Relationship (ER) Diagram of PostgreSQL/TimescaleDB Hydrological Schema", "31"),
    ("3.5", "Dynamic Evacuation Road Network Topology with Obstacle-Avoiding Edge Weights", "34"),
    ("4.1", "ESP32 Hardware Breadboard Wiring and MicroPython REPL Initialization in Wokwi Simulation", "37"),
    ("4.2", "Next.js Public Citizen Portal Displaying Safe Dijkstra Evacuation Route to Designated Relief Shelter", "41"),
    ("4.3", "Next.js Operator SCADA Operations Portal Command Center with Live SCADA Telemetry", "43"),
    ("6.1", "High-Frequency Ultrasonic Distance and Depth Telemetry Serial Log during Drainage Inundation", "56"),
    ("6.2", "Wokwi Distance Slider Calibration at 400cm with Green LED Active and Gate at 0° (Normal State)", "57"),
    ("6.3", "Operator Ops Command Center Showing Kapilatheertham Nallah in Critical State (174.8cm / 180cm, Gate 90° Closed)", "59"),
    ("6.4", "Operator Dashboard Detailed Node Telemetry Modal and 6-Hour Water Level Trend Sparkline", "60"),
    ("6.5", "Multi-Drain SCADA Overview During Simulated Flash Flood Storm Scenario", "62"),
]

TABLES = [
    ("1.1", "Tirupati Regional Flashpoint Drainage Inventory and Physical Sensor Mount Specifications", "9"),
    ("2.1", "Comparative Analysis of State-of-the-Art Urban Flood Monitoring Approaches", "19"),
    ("3.1", "ESP32 Microcontroller GPIO Pin Mapping and Peripheral Assignment", "23"),
    ("3.2", "MQTT Topic Hierarchy and Payload Protocol Definitions", "26"),
    ("3.3", "Relational and Time-Series Database Schema Specifications", "30"),
    ("3.4", "Dynamic Evacuation Road Network Node Coordinates and Graph Edge Distances", "33"),
    ("4.1", "Multi-Tier Risk Evaluation Thresholds and Autonomous Edge Control Rules", "39"),
    ("4.2", "Multilingual Citizen Emergency Notification Template Specifications", "44"),
    ("5.1", "Work Breakdown Structure (WBS) Task Distribution Matrix Across Project Phases", "46"),
    ("5.2", "Project Development Timeline and Milestone Execution Schedule", "48"),
    ("5.3", "Comprehensive Hardware Bill of Materials (BOM) and Cost Estimation", "50"),
    ("5.4", "Failure Mode and Effects Analysis (FMEA) for Critical System Subsystems", "52"),
    ("6.1", "Ultrasonic Distance Sensor Calibration and Depth Accuracy Experimental Results", "55"),
    ("6.2", "MQTT Telemetry Transmission Latency and Packet Delivery Ratio under Varying Network Conditions", "58"),
    ("6.3", "Edge Autonomous Actuation vs. Cloud Manual Override Latency Benchmark", "61"),
    ("6.4", "Dijkstra Evacuation Routing Computational Efficiency and Path Safety Margin Evaluation", "63"),
    ("6.5", "Automated System Verification Test Suite Execution Results (28 Tests Passed)", "64"),
]

TOC_ENTRIES = [
    ("Abstract", "1"),
    ("List of Acronyms", "2"),
    ("List of Figures", "3"),
    ("List of Tables", "4"),
    ("Chapter 1 Introduction", "5"),
    ("  1.1 Introduction", "5"),
    ("  1.2 Regional Catchment Analysis: Swarnamukhi Basin & Foothills", "7"),
    ("  1.3 Problem Statement", "9"),
    ("  1.4 Objectives of the Investigation", "10"),
    ("  1.5 Scope of the Project", "10"),
    ("  1.6 Real-World Applications & Societal Value", "11"),
    ("  1.7 Limitations & Operational Constraints", "11"),
    ("Chapter 2 Literature Survey", "12"),
    ("  2.1 Evolution of Urban Drainage and Flood Monitoring Systems", "12"),
    ("  2.2 Wireless Sensor Networks and Hydrological Telemetry", "13"),
    ("  2.3 Edge Computing and Autonomous Failsafe Actuation", "15"),
    ("  2.4 Communication Protocol Comparison: MQTT vs. HTTP/REST", "16"),
    ("  2.5 Time-Series Data Management & Continuous Aggregates", "18"),
    ("  2.6 Dynamic Graph Routing and Evacuation Navigation", "18"),
    ("  2.7 Multilingual Emergency Alerting Frameworks", "19"),
    ("  2.8 Summary of Research Gaps and Problem Formulation", "19"),
    ("Chapter 3 Analysis & Design", "20"),
    ("  3.1 Requirement Analysis (Functional & Non-Functional)", "20"),
    ("  3.2 Overall System Architecture & Data Flow", "21"),
    ("  3.3 Hardware Subsystem Design", "22"),
    ("  3.4 Pin Configuration and Circuit Schematic Design", "23"),
    ("  3.5 Firmware Architecture & Finite State Machine (FSM)", "24"),
    ("  3.6 Cloud Backend Microservices Architecture", "27"),
    ("  3.7 Time-Series Database Schema & Hypertable Partitioning", "29"),
    ("  3.8 Risk Assessment Engine & Mathematical Formulation", "31"),
    ("  3.9 Dynamic Dijkstra Evacuation Routing Formulation", "32"),
    ("  3.10 Multilingual Notification Gateway Design", "34"),
    ("Chapter 4 Implementation", "35"),
    ("  4.1 Physical ESP32 Hardware Integration & Wokwi Simulation Setup", "35"),
    ("  4.2 Firmware Implementation in C++ (PlatformIO) and MicroPython", "36"),
    ("  4.3 MQTT Message Broker Setup & Topic Hierarchy", "38"),
    ("  4.4 FastAPI Asynchronous Backend Services", "39"),
    ("  4.5 TimescaleDB Initialization, Continuous Aggregates & Audit Logging", "40"),
    ("  4.6 Next.js Operator SCADA Operations Portal", "42"),
    ("  4.7 Public Citizen Evacuation Portal & Interactive Routing Map", "43"),
    ("  4.8 Automated Multi-Node Flash Flood Simulation Script", "44"),
    ("Chapter 5 Project Management", "45"),
    ("  5.1 Work Breakdown Structure (WBS)", "45"),
    ("  5.2 Project Timeline & Milestones (Gantt Schedule)", "47"),
    ("  5.3 Cost Estimation, Bill of Materials (BOM) & Budgeting", "49"),
    ("  5.4 Risk Management, Failsafe Redundancy & FMEA", "51"),
    ("  5.5 Sustainability, Environmental & Community Impact Assessment", "53"),
    ("Chapter 6 Results & Performance Evaluation", "55"),
    ("  6.1 Telemetry Sensor Calibration & Accuracy Evaluation", "55"),
    ("  6.2 Telemetry Transmission Latency & Packet Delivery Ratio", "57"),
    ("  6.3 Edge Failsafe Actuation Response Time & Servo Horn Performance", "58"),
    ("  6.4 Risk Engine Hysteresis & False Alarm Suppression Testing", "60"),
    ("  6.5 Dynamic Dijkstra Evacuation Routing Validation", "62"),
    ("  6.6 Multilingual Notification Dispatch Latency & Provider Evaluation", "63"),
    ("  6.7 End-to-End Automated Monorepo Verification (28/28 Pytest Suite)", "64"),
    ("Chapter 7 Conclusions and Future Work", "65"),
    ("  7.1 Conclusions", "65"),
    ("  7.2 Future Work", "65"),
    ("References", "66"),
    ("Appendix: Complete Program Source Code", "67"),
    ("Research Paper Outline / Manuscript Draft", "78"),
    ("BIO-DATA", "80"),
]
