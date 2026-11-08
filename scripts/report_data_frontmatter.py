# report_data_frontmatter.py
"""
Front matter definitions for the Mohan Babu University (MBU) TESP Project Report.
Updated with clean title: SMART COMMUNITY FLOOD & URBAN DRAINAGE EARLY WARNING SYSTEM
Synchronized with expanded page numbers across the 60+ page report.
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

STUDENT_BIOS = [
    {
        "name": "Lagisetty Vidya Charan",
        "roll": "23101A030061",
        "father": "L. Chandrasekhar",
        "dob": "14/12/2005",
        "branch": "B.Tech - Electronics & Communication Engineering",
        "institution": "Mohan Babu University, Sree Sainath Nagar, Tirupati – 517 102",
        "nationality": "Indian",
        "phone": "+91-98765 43210",
        "email": "charan.lagisetty@mbu.asia",
        "address": "Department of ECE, School of Engineering, Mohan Babu University, Tirupati – 517 102",
        "linkedin": "linkedin.com/in/vidyacharan-lagisetty",
    },
    {
        "name": "Kummara Nandakishore",
        "roll": "23101A030035",
        "father": "K. Venkataswamy",
        "dob": "22/08/2005",
        "branch": "B.Tech - Electronics & Communication Engineering",
        "institution": "Mohan Babu University, Sree Sainath Nagar, Tirupati – 517 102",
        "nationality": "Indian",
        "phone": "+91-98765 43211",
        "email": "nandakishore.k@mbu.asia",
        "address": "Department of ECE, School of Engineering, Mohan Babu University, Tirupati – 517 102",
        "linkedin": "linkedin.com/in/nandakishore-kummara",
    },
    {
        "name": "Tajuddin Mohammad Ashraf",
        "roll": "23101A030001",
        "father": "T. Mohammad Rafi",
        "dob": "05/03/2005",
        "branch": "B.Tech - Electronics & Communication Engineering",
        "institution": "Mohan Babu University, Sree Sainath Nagar, Tirupati – 517 102",
        "nationality": "Indian",
        "phone": "+91-98765 43212",
        "email": "ashraf.tajuddin@mbu.asia",
        "address": "Department of ECE, School of Engineering, Mohan Babu University, Tirupati – 517 102",
        "linkedin": "linkedin.com/in/ashraf-tajuddin",
    },
    {
        "name": "Shaik Sufiyan",
        "roll": "23101A030050",
        "father": "Shaik Abdul Sattar",
        "dob": "19/11/2005",
        "branch": "B.Tech - Electronics & Communication Engineering",
        "institution": "Mohan Babu University, Sree Sainath Nagar, Tirupati – 517 102",
        "nationality": "Indian",
        "phone": "+91-98765 43213",
        "email": "sufiyan.shaik@mbu.asia",
        "address": "Department of ECE, School of Engineering, Mohan Babu University, Tirupati – 517 102",
        "linkedin": "linkedin.com/in/sufiyan-shaik",
    },
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
    ("1.1", "Geographical Catchment Map of Seshachalam Foothills and Swarnamukhi Drainage Basin in Tirupati", "13"),
    ("1.2", "High-Level Conceptual Block Diagram of the flood-ews Early Warning System", "14"),
    ("2.1", "Architectural Evolution of Hydrological Telemetry from Manual Gauges to Autonomous Edge IoT", "20"),
    ("2.2", "Communication Protocol Latency and Overhead Comparison: MQTT Publish-Subscribe vs. HTTP Polling", "23"),
    ("3.1", "Complete Circuit Schematic and Pin Interconnections of the ESP32 Drainage Telemetry Node", "31"),
    ("3.2", "Finite State Machine (FSM) State Transition Diagram for Autonomous Edge Floodgate Control", "32"),
    ("3.3", "End-to-End System Microservices Architecture and Cloud Message Broker Topology", "33"),
    ("3.4", "Entity-Relationship (ER) Diagram of PostgreSQL/TimescaleDB Hydrological Schema", "34"),
    ("3.5", "Dynamic Evacuation Road Network Topology with Obstacle-Avoiding Edge Weights", "37"),
    ("4.1", "ESP32 Hardware Breadboard Wiring and MicroPython REPL Initialization in Wokwi Simulation", "39"),
    ("4.2", "Next.js Operator SCADA Operations Portal Command Center with Live Inundation Alert", "45"),
    ("4.3", "Next.js Public Citizen Portal Displaying Safe Dijkstra Evacuation Route to Designated Relief Shelter", "47"),
    ("6.1", "High-Frequency Ultrasonic Distance and Depth Telemetry Serial Log during Drainage Inundation", "56"),
    ("6.2", "Wokwi Distance Slider Calibration at 400cm with Green LED Active and Gate at 0° (Normal State)", "57"),
    ("6.3", "Operator Ops Command Center Showing Kapilatheertham Nallah in Critical State (174.8cm / 180cm, Gate 90° Closed)", "60"),
    ("6.4", "Operator Dashboard Detailed Node Telemetry Modal and 6-Hour Water Level Trend Sparkline", "61"),
    ("6.5", "Multi-Drain SCADA Overview During Simulated Flash Flood Storm Scenario", "64"),
]

TABLES = [
    ("1.1", "Tirupati Regional Flashpoint Drainage Inventory and Physical Sensor Mount Specifications", "14"),
    ("2.1", "Comparative Analysis of State-of-the-Art Urban Flood Monitoring Approaches", "26"),
    ("3.1", "ESP32 Microcontroller GPIO Pin Mapping and Peripheral Assignment", "31"),
    ("3.2", "MQTT Topic Hierarchy and Payload Protocol Definitions", "33"),
    ("3.3", "Relational and Time-Series Database Schema Specifications", "34"),
    ("3.4", "Dynamic Evacuation Road Network Node Coordinates and Graph Edge Distances", "37"),
    ("4.1", "Multi-Tier Risk Evaluation Thresholds and Autonomous Edge Control Rules", "43"),
    ("4.2", "Multilingual Citizen Emergency Notification Template Specifications", "48"),
    ("5.1", "Work Breakdown Structure (WBS) Task Distribution Matrix Across Project Phases", "49"),
    ("5.2", "Project Development Timeline and Milestone Execution Schedule", "50"),
    ("5.3", "Comprehensive Hardware Bill of Materials (BOM) and Cost Estimation", "51"),
    ("5.4", "Failure Mode and Effects Analysis (FMEA) for Critical System Subsystems", "53"),
    ("6.1", "Ultrasonic Distance Sensor Calibration and Depth Accuracy Experimental Results", "56"),
    ("6.2", "MQTT Telemetry Transmission Latency and Packet Delivery Ratio under Varying Network Conditions", "58"),
    ("6.3", "Edge Autonomous Actuation vs. Cloud Manual Override Latency Benchmark", "59"),
    ("6.4", "Dijkstra Evacuation Routing Computational Efficiency and Path Safety Margin Evaluation", "63"),
    ("6.5", "Automated System Verification Test Suite Execution Results (28 Tests Passed)", "65"),
]

TOC_ENTRIES = [
    ("Abstract", "1"),
    ("List of Acronyms", "2"),
    ("List of Figures", "3"),
    ("List of Tables", "4"),
    ("Chapter 1 Introduction", "12"),
    ("  1.1 Introduction", "12"),
    ("  1.2 Regional Catchment Analysis: Swarnamukhi Basin & Foothills", "13"),
    ("  1.3 Problem Statement", "15"),
    ("  1.4 Objectives of the Investigation", "16"),
    ("  1.5 Scope of the Project", "17"),
    ("  1.6 Real-World Applications & Societal Value", "17"),
    ("  1.7 Limitations & Operational Constraints", "18"),
    ("Chapter 2 Literature Survey", "19"),
    ("  2.1 Evolution of Urban Drainage and Flood Monitoring Systems", "19"),
    ("  2.2 Wireless Sensor Networks and Hydrological Telemetry", "20"),
    ("  2.3 Edge Computing and Autonomous Failsafe Actuation", "21"),
    ("  2.4 Communication Protocol Comparison: MQTT vs. HTTP/REST", "22"),
    ("  2.5 Time-Series Data Management & Continuous Aggregates", "23"),
    ("  2.6 Dynamic Graph Routing and Evacuation Navigation", "24"),
    ("  2.7 Multilingual Emergency Alerting Frameworks", "25"),
    ("  2.8 Summary of Research Gaps and Problem Formulation", "26"),
    ("Chapter 3 Analysis & Design", "27"),
    ("  3.1 Requirement Analysis (Functional & Non-Functional)", "27"),
    ("  3.2 Overall System Architecture & Data Flow", "29"),
    ("  3.3 Hardware Subsystem Design", "30"),
    ("  3.4 Pin Configuration and Circuit Schematic Design", "31"),
    ("  3.5 Firmware Architecture & Finite State Machine (FSM)", "32"),
    ("  3.6 Cloud Backend Microservices Architecture", "33"),
    ("  3.7 Time-Series Database Schema & Hypertable Partitioning", "34"),
    ("  3.8 Risk Assessment Engine & Mathematical Formulation", "35"),
    ("  3.9 Dynamic Dijkstra Evacuation Routing Formulation", "36"),
    ("  3.10 Multilingual Notification Gateway Design", "37"),
    ("Chapter 4 Implementation", "38"),
    ("  4.1 Physical ESP32 Hardware Integration & Wokwi Simulation Setup", "38"),
    ("  4.2 Firmware Implementation in C++ (PlatformIO) and MicroPython", "40"),
    ("  4.3 MQTT Message Broker Setup & Topic Hierarchy", "41"),
    ("  4.4 FastAPI Asynchronous Backend Services", "42"),
    ("  4.5 TimescaleDB Initialization, Continuous Aggregates & Audit Logging", "43"),
    ("  4.6 Next.js Operator SCADA Operations Portal", "44"),
    ("  4.7 Public Citizen Evacuation Portal & Interactive Routing Map", "46"),
    ("  4.8 Automated Multi-Node Flash Flood Simulation Script", "48"),
    ("Chapter 5 Project Management", "49"),
    ("  5.1 Work Breakdown Structure (WBS)", "49"),
    ("  5.2 Project Timeline & Milestones (Gantt Schedule)", "50"),
    ("  5.3 Cost Estimation, Bill of Materials (BOM) & Budgeting", "51"),
    ("  5.4 Risk Management, Failsafe Redundancy & FMEA", "52"),
    ("  5.5 Sustainability, Environmental & Community Impact Assessment", "54"),
    ("Chapter 6 Results & Performance Evaluation", "55"),
    ("  6.1 Telemetry Sensor Calibration & Accuracy Evaluation", "55"),
    ("  6.2 Telemetry Transmission Latency & Packet Delivery Ratio", "58"),
    ("  6.3 Edge Failsafe Actuation Response Time & Servo Horn Performance", "59"),
    ("  6.4 Risk Engine Hysteresis & False Alarm Suppression Testing", "62"),
    ("  6.5 Dynamic Dijkstra Evacuation Routing Validation", "63"),
    ("  6.6 Multilingual Notification Dispatch Latency & Provider Evaluation", "64"),
    ("  6.7 End-to-End Automated Monorepo Verification (28/28 Pytest Suite)", "65"),
    ("Chapter 7 Conclusions and Future Work", "66"),
    ("  7.1 Conclusions", "66"),
    ("  7.2 Future Work", "68"),
    ("References", "69"),
    ("Appendix: Complete Program Source Code", "72"),
    ("  A.1 ESP32 MicroPython Firmware (main.py)", "72"),
    ("  A.2 ESP32 C++ Arduino Framework Firmware (sketch.ino)", "75"),
    ("  A.3 Hydrological Risk Assessment Engine (risk.py)", "78"),
    ("  A.4 Dynamic Dijkstra Evacuation Routing Service (evacuation.py)", "80"),
    ("  A.5 Multilingual Citizen Notification Gateway (alerts.py)", "83"),
    ("  A.6 Database Initialization & Hypertable Seed Script (init.sql)", "85"),
    ("Research Paper Outline / Manuscript Draft", "87"),
    ("BIO-DATA", "89"),
]
