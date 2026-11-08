# build_markdown_report.py
"""
Generates the comprehensive Markdown artifact for the MBU TESP Project Report.
Refactored to match exact student details, supervisor Dr. N. Gireesh, and unabridged code.
Outputs to:
C:\\Users\\lagis\\.gemini\\antigravity\\brain\\423ccfeb-6e73-4ebd-ac74-a55be441797b\\MBU_TESP_Project_Report_Flood_EWS.md
"""

import os
import report_data_frontmatter as fm
import report_data_ch1_ch2 as c12
import report_data_ch3_ch4 as c34
import report_data_ch5_ch6_ch7 as c567
import report_data_appendix as appx

OUT_MD_PATH = r"C:\Users\lagis\.gemini\antigravity\brain\423ccfeb-6e73-4ebd-ac74-a55be441797b\MBU_TESP_Project_Report_Flood_EWS.md"

def table_to_md(headers, rows):
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("\n", " ") for c in r) + " |")
    return "\n".join(out)

def read_file_safely(rel_path):
    try:
        full_path = os.path.join(r"C:\Users\lagis\Documents\Community Project", rel_path)
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"# Code file {rel_path} could not be loaded: {e}"

def main():
    md = []
    
    # Title & Front Matter
    md.append(f"# {fm.PROJECT_TITLE}\n\n")
    md.append("**A TESP Project Report submitted to Mohan Babu University**  \n*In partial fulfilment of the requirements for the award of the degree of*  \n**BACHELOR OF TECHNOLOGY IN ELECTRONICS AND COMMUNICATION ENGINEERING**\n\n")
    md.append("### Submitted by:\n\n")
    md.append("| Student Name | Roll Number |\n| :--- | :--- |\n")
    for name, roll in fm.STUDENTS:
        md.append(f"| {name} | {roll} |\n")
    md.append("\n### Under the Esteemed Supervision of:\n**Dr. N. Gireesh, M.Tech, Ph.D.**  \nProfessor, CoE, Department of ECE\n\n")
    md.append("---\n\n### Mohan Babu University\n*Department of Electronics and Communication Engineering, School of Engineering*  \nSree Sainath Nagar, Tirupati – 517 102 | Academic Year: 2026 – 2027\n\n---\n")
    
    # Certificate
    md.append("## CERTIFICATE\n\n")
    md.append(
        "This is to certify that the TESP Project report titled **“SMART COMMUNITY FLOOD & URBAN DRAINAGE EARLY WARNING SYSTEM”** "
        "is the bonafide work done by:\n\n"
    )
    for name, roll in fm.STUDENTS:
        md.append(f"- **{name} ({roll})**\n")
    md.append(
        "\nin the Department of Electronics and Communication Engineering, submitted to Mohan Babu University, Tirupati in partial fulfilment "
        "of the requirements for the degree of Bachelor of Technology in ECE during the academic year 2026–2027. This work has been carried out "
        "under my guidance and supervision. The results embodied in this project report have not been submitted to any other University or Organization "
        "for the award of any degree or diploma.\n\n"
    )
    md.append("| Supervisor | Head of Department |\n| :--- | :--- |\n| **Dr. N. Gireesh, M.Tech, Ph.D.**<br>Professor, CoE, Dept. of ECE | **Dr. N. Sudhakar Reddy, M.Tech, Ph.D.**<br>Professor & Head, Dept. of ECE |\n\n")
    md.append("**INTERNAL EXAMINER** &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; **EXTERNAL EXAMINER**\n\n---\n")

    # Acknowledgement
    md.append("## ACKNOWLEDGEMENT\n\n")
    md.append(
        "We are extremely thankful to our beloved Chancellor, **Dr. M. Mohan Babu Garu**, for his inspiration and unwavering commitment to academic growth and student development.\n\n"
        "We express sincere gratitude to our Pro-Chancellor, **Sri Vishnu Manchu Garu**, for his constant encouragement and visionary leadership in fostering a culture of learning and excellence.\n\n"
        "We express sincere gratitude to our Hon’ble Vice-Chancellor, **Prof. P.V Ramana Garu**, for his valuable guidance, encouragement, and continuous support in all academic endeavours.\n\n"
        "We are highly indebted to **Dr. S. Babu Devasenapati**, Dean-School of Engineering & Computing, for his valuable support and guidance in all academic matters.\n\n"
        "We are deeply obliged to **Dr. N. Sudhakar Reddy**, Professor & Head, Department of ECE, for his motivation, insightful guidance, and persistent encouragement.\n\n"
        "We extend heartfelt thanks to our supervisor, **Dr. N. Gireesh, M.Tech, Ph.D.**, Professor, CoE, Department of ECE, for the consistent support, insightful guidance, and constructive feedback provided during the project work.\n\n"
    )
    for name, roll in fm.STUDENTS:
        md.append(f"- **{name} ({roll})**\n")
    md.append("\n---\n")

    # Declaration
    md.append("## DECLARATION\n\n")
    md.append(
        "We hereby declare that this TESP project report titled **“SMART COMMUNITY FLOOD & URBAN DRAINAGE EARLY WARNING SYSTEM”** "
        "is a genuine project work carried out by us in the B.Tech (Electronics and Communication Engineering) degree course of Mohan Babu University, "
        "Tirupati, and has not been submitted to any other course or university for the award of any degree.\n\n"
    )
    for name, roll in fm.STUDENTS:
        md.append(f"- **{name} ({roll})**\n")
    md.append("\n---\n")

    # Abstract
    md.append("## ABSTRACT\n\n")
    md.append(f"{fm.ABSTRACT_TEXT}\n\n---\n")

    # Acronyms
    md.append("## LIST OF ACRONYMS\n\n")
    md.append(table_to_md(["Acronym", "Definition"], fm.ACRONYMS))
    md.append("\n\n---\n")

    # Figures
    md.append("## LIST OF FIGURES\n\n")
    md.append(table_to_md(["Figure No.", "Description", "Page No."], fm.FIGURES))
    md.append("\n\n---\n")

    # Tables
    md.append("## LIST OF TABLES\n\n")
    md.append(table_to_md(["Table No.", "Description", "Page No."], fm.TABLES))
    md.append("\n\n---\n")

    # Table of Contents
    md.append("## TABLE OF CONTENTS\n\n")
    md.append(table_to_md(["Chapter / Section", "Page No."], fm.TOC_ENTRIES))
    md.append("\n\n---\n")

    # Chapter 1
    md.append("# CHAPTER 1\n# INTRODUCTION\n\n")
    md.append("## 1.1 Introduction\n\n")
    for p in c12.CH1_INTRO:
        md.append(f"{p}\n\n")
    md.append("## 1.2 Regional Catchment Analysis: Swarnamukhi Basin & Foothills\n\n")
    for p in c12.CH1_REGIONAL_ANALYSIS:
        md.append(f"{p}\n\n")
    md.append("### Table 1.1: Tirupati Regional Flashpoint Drainage Inventory\n\n")
    md.append(table_to_md(["Node ID", "Flashpoint Name", "Latitude", "Longitude", "Ward", "Mount Ht", "Capacity", "Context"], c12.TABLE_1_1_DATA))
    md.append("\n\n## 1.3 Problem Statement\n\n")
    for p in c12.CH1_PROBLEM_STATEMENT:
        md.append(f"{p}\n\n")
    for item in c12.CH1_PROBLEM_ITEMS:
        md.append(f"- {item}\n\n")
    md.append("## 1.4 Objectives of the Investigation\n\n")
    md.append(f"{c12.CH1_OBJECTIVES_INTRO}\n\n")
    for item in c12.CH1_OBJECTIVES_ITEMS:
        md.append(f"- {item}\n\n")
    md.append(f"## 1.5 Scope of the Project\n\n{c12.CH1_SCOPE}\n\n")
    md.append(f"## 1.6 Real-World Applications & Societal Value\n\n{c12.CH1_APPLICATIONS_INTRO}\n\n")
    for item in c12.CH1_APPLICATIONS_ITEMS:
        md.append(f"- {item}\n\n")
    md.append(f"## 1.7 Limitations & Operational Constraints\n\n{c12.CH1_LIMITATIONS_INTRO}\n\n")
    for item in c12.CH1_LIMITATIONS_ITEMS:
        md.append(f"- {item}\n\n")

    md.append("---\n\n")

    # Chapter 2
    md.append("# CHAPTER 2\n# LITERATURE SURVEY\n\n")
    for title, paras in c12.CH2_LITERATURE_SURVEY:
        md.append(f"## {title}\n\n")
        for p in paras:
            md.append(f"{p}\n\n")
        if "2.4" in title:
            md.append(f"{c12.CH2_MQTT_TIERS_INTRO}\n\n")
            for tier in c12.CH2_MQTT_TIERS:
                md.append(f"- {tier}\n\n")
            md.append(f"{c12.CH2_MQTT_CONCLUSION}\n\n")

    for title, paras in c12.CH2_REMAINING_SECTIONS:
        md.append(f"## {title}\n\n")
        for p in paras:
            md.append(f"{p}\n\n")

    md.append(f"## 2.8 Summary of Research Gaps and Problem Formulation\n\n{c12.CH2_RESEARCH_GAPS_INTRO}\n\n")
    for gap in c12.CH2_RESEARCH_GAPS:
        md.append(f"- {gap}\n\n")
    md.append(f"{c12.CH2_RESEARCH_GAPS_CONCLUSION}\n\n")

    md.append("### Table 2.1: Comparative Analysis of State-of-the-Art Approaches\n\n")
    md.append(table_to_md(["Monitoring Paradigm", "Sensor Type", "Protocol", "Processing Tier", "Edge Actuation", "Routing", "Database", "Alerts", "Cost"], c12.TABLE_2_1_DATA))
    md.append("\n\n---\n\n")

    # Chapter 3
    md.append("# CHAPTER 3\n# ANALYSIS & DESIGN\n\n")
    md.append(f"## 3.1 Requirement Analysis\n\n{c34.CH3_REQ_INTRO}\n\n### {c34.CH3_FR_INTRO}\n\n")
    for item in c34.CH3_FR_ITEMS:
        md.append(f"- {item}\n\n")
    md.append(f"### {c34.CH3_NFR_INTRO}\n\n")
    for item in c34.CH3_NFR_ITEMS:
        md.append(f"- {item}\n\n")

    md.append(f"## 3.2 Overall System Architecture & Data Flow\n\n{c34.CH3_ARCH_INTRO}\n\n")
    for layer in c34.CH3_ARCH_LAYERS:
        md.append(f"- {layer}\n\n")

    md.append("## 3.3 Hardware Subsystem Design\n\n")
    for p in c34.CH3_HARDWARE[:3]:
        md.append(f"{p}\n\n")

    md.append(f"## 3.4 Pin Configuration and Circuit Schematic Design\n\n{c34.CH3_HARDWARE[3]}\n\n")
    md.append("### Table 3.1: ESP32 Microcontroller GPIO Pin Mapping\n\n")
    md.append(table_to_md(["Signal Name", "ESP32 Pin", "Direction", "Functional Description", "Wire Color"], c34.TABLE_3_1_DATA))
    md.append("\n\n")

    md.append(f"## 3.5 Firmware Architecture & Finite State Machine (FSM)\n\n{c34.CH3_FSM_INTRO}\n\n### {c34.CH3_FSM_LOGIC_INTRO}\n\n")
    for item in c34.CH3_FSM_LOGIC_ITEMS:
        md.append(f"- {item}\n\n")

    md.append(f"## 3.6 Cloud Backend Microservices Architecture\n\n{c34.CH3_BACKEND_INTRO}\n\n")
    for task in c34.CH3_BACKEND_TASKS:
        md.append(f"- {task}\n\n")

    md.append(f"## 3.7 Time-Series Database Schema & Hypertable Partitioning\n\n{c34.CH3_TIMESCALEDB}\n\n")
    md.append("### Table 3.3: Relational and Time-Series Database Schema Specifications\n\n")
    md.append(table_to_md(["Table Name", "Primary / Foreign Keys", "Storage Engine & Column Definitions"], c34.TABLE_3_3_DATA))
    md.append("\n\n")

    md.append("## 3.8 Risk Assessment Engine & Mathematical Formulation\n\n")
    for p in c34.CH3_RISK_FORMULATION:
        md.append(f"{p}\n\n")
    md.append(f"### {c34.CH3_HYSTERESIS_INTRO}\n\n")
    for rule in c34.CH3_HYSTERESIS_RULES:
        md.append(f"- {rule}\n\n")

    md.append("## 3.9 Dynamic Dijkstra Evacuation Routing Formulation\n\n")
    for p in c34.CH3_DIJKSTRA:
        md.append(f"{p}\n\n")
    md.append("### Table 3.4: Dynamic Road Network Graph Edge Specifications\n\n")
    md.append(table_to_md(["Node ID", "Flashpoint Name", "Latitude", "Longitude", "Destination Shelter", "Dist (Normal vs Flood)"], c34.TABLE_3_4_DATA))
    md.append("\n\n---\n\n")

    # Chapter 4
    md.append("# CHAPTER 4\n# IMPLEMENTATION\n\n")
    for title, paras in c34.CH4_SECTIONS:
        md.append(f"## {title}\n\n")
        for p in paras:
            md.append(f"{p}\n\n")
    md.append("### Table 4.2: Multilingual Emergency Notification Template Specifications\n\n")
    md.append(table_to_md(["Target Language", "Standardized Dynamic Citizen Notification Template"], c34.TABLE_4_2_DATA))
    md.append("\n\n---\n\n")

    # Chapter 5
    md.append("# CHAPTER 5\n# PROJECT MANAGEMENT\n\n")
    md.append(f"## 5.1 Work Breakdown Structure (WBS)\n\n{c567.CH5_WBS_INTRO}\n\n")
    md.append(table_to_md(["WBS Code", "Work Package Name", "Scope of Engineering Deliverables", "Assigned Lead"], c567.TABLE_5_1_DATA))
    md.append(f"\n\n## 5.2 Project Timeline & Milestones\n\n{c567.CH5_TIMELINE_INTRO}\n\n")
    md.append(table_to_md(["Milestone Phase", "Target Timeline", "Engineering Accomplishments"], c567.TABLE_5_2_DATA))
    md.append(f"\n\n## 5.3 Cost Estimation, Bill of Materials (BOM) & Budgeting\n\n{c567.CH5_BOM_INTRO}\n\n")
    md.append(table_to_md(["Component Description", "Specifications", "Qty", "Unit Cost", "Subtotal"], c567.TABLE_5_3_DATA))
    md.append(f"\n\n## 5.4 Risk Management & FMEA\n\n{c567.CH5_FMEA_INTRO}\n\n")
    md.append(table_to_md(["Failure Mode", "Operational Effect", "S", "O", "D", "RPN", "Safeguard"], c567.TABLE_5_4_DATA))
    md.append(f"\n\n## 5.5 Sustainability & Community Impact\n\n{c567.CH5_SUSTAINABILITY_INTRO}\n\n")
    for item in c567.CH5_SUSTAINABILITY_ITEMS:
        md.append(f"- {item}\n\n")

    md.append("---\n\n")

    # Chapter 6
    md.append("# CHAPTER 6\n# RESULTS & PERFORMANCE EVALUATION\n\n")
    md.append(f"## 6.1 Telemetry Sensor Calibration & Accuracy Evaluation\n\n{c567.CH6_CALIBRATION_INTRO}\n\n")
    md.append(table_to_md(["Mount Ht", "True Depth", "Sensor Dist", "Computed Depth", "Abs Error", "Rel Error %"], c567.TABLE_6_1_DATA))
    md.append(f"\n\n## 6.2 Telemetry Transmission Latency & Packet Delivery Ratio\n\n{c567.CH6_LATENCY_INTRO}\n\n")
    md.append(table_to_md(["Network Interface", "Test Cycles", "Mean Latency", "Min Latency", "Max Latency", "PDR"], c567.TABLE_6_2_DATA))
    md.append(f"\n\n## 6.3 Edge Failsafe Actuation Response Time & Servo Horn Performance\n\n{c567.CH6_ACTUATION_INTRO}\n\n")
    md.append(table_to_md(["Operational Mode", "Mean Latency", "Min", "Max", "Success Rate", "Observations"], c567.TABLE_6_3_DATA))
    md.append(f"\n\n## 6.4 Risk Engine Hysteresis & False Alarm Suppression Testing\n\n{c567.CH6_HYSTERESIS_EVAL}\n\n")
    md.append(f"## 6.5 Dynamic Dijkstra Evacuation Routing Validation\n\n{c567.CH6_DIJKSTRA_EVAL}\n\n")
    md.append(table_to_md(["Origin Node", "Flood State", "Destination Shelter", "Distance", "Time", "Strategy"], c567.TABLE_6_4_DATA))
    md.append(f"\n\n## 6.6 Multilingual Notification Dispatch Latency & Provider Evaluation\n\n{c567.CH6_ALERT_EVAL}\n\n")
    md.append(f"## 6.7 End-to-End Automated Monorepo Verification (28/28 Pytest Suite)\n\n{c567.CH6_VERIFICATION_INTRO}\n\n")
    md.append(table_to_md(["Test Name", "File Location", "Result", "Assertion Scope"], c567.TABLE_6_5_DATA))
    md.append("\n\n---\n\n")

    # Chapter 7
    md.append("# CHAPTER 7\n# CONCLUSIONS AND FUTURE WORK\n\n")
    md.append(f"## 7.1 Conclusions\n\n{c567.CH7_CONCLUSIONS_INTRO}\n\n### {c567.CH7_ACHIEVEMENTS_INTRO}\n\n")
    for item in c567.CH7_ACHIEVEMENTS:
        md.append(f"- {item}\n\n")
    md.append(f"## 7.2 Future Work\n\n{c567.CH7_FUTURE_WORK_INTRO}\n\n")
    for item in c567.CH7_FUTURE_WORK_ITEMS:
        md.append(f"- {item}\n\n")

    md.append("---\n\n")

    # References
    md.append("# REFERENCES\n\n")
    for r in appx.REFERENCES:
        md.append(f"{r}  \n")
    md.append("\n---\n\n")

    # Appendix
    md.append("# APPENDIX\n# SAMPLE PROGRAM CODE\n\n")
    md.append("## A.1 ESP32 MicroPython Firmware (firmware/main.py)\n\n```python\n")
    md.append(read_file_safely("firmware/main.py") + "\n```\n\n")
    md.append("## A.2 ESP32 C++ Arduino Framework Firmware (firmware/sketch.ino)\n\n```cpp\n")
    md.append(read_file_safely("firmware/sketch.ino") + "\n```\n\n")
    md.append("## A.3 Hydrological Risk Assessment Engine (backend/app/risk.py)\n\n```python\n")
    md.append(read_file_safely("backend/app/risk.py") + "\n```\n\n")
    md.append("## A.4 Dynamic Dijkstra Evacuation Routing Service (backend/app/evacuation.py)\n\n```python\n")
    md.append(read_file_safely("backend/app/evacuation.py") + "\n```\n\n")
    md.append("## A.5 Multilingual Citizen Notification Gateway (backend/app/alerts.py)\n\n```python\n")
    md.append(read_file_safely("backend/app/alerts.py") + "\n```\n\n")
    md.append("## A.6 Database Initialization & Hypertable Seed Script (db/init.sql)\n\n```sql\n")
    md.append(read_file_safely("db/init.sql") + "\n```\n\n")

    # Research Paper
    md.append("# RESEARCH PAPERS PUBLISHED\n\n")
    for item in appx.RESEARCH_PAPER_TEXT:
        md.append(f"{item}\n\n")

    # Bio-Data
    md.append("---\n\n# BIO-DATA\n\n")
    md.append("| Field | Details |\n| :--- | :--- |\n| **NAME** | Lagisetty Vidya Charan (23101A030061) |\n| **BRANCH & DEPT** | B.Tech - Electronics & Communication Engineering |\n| **INSTITUTION** | Mohan Babu University, Tirupati – 517 102 |\n| **NATIONALITY** | Indian |\n\n")
    md.append("### CONTACT DETAILS\n\n| Field | Details |\n| :--- | :--- |\n| **Contact No.** | +91-XXXXXXXXXX |\n| **Email** | student@mbu.asia |\n| **Contact Address** | Department of ECE, Mohan Babu University, Sree Sainath Nagar, Tirupati – 517 102 |\n| **Project Team** | Lagisetty Vidya Charan, Kummara Nandakishore, Tajuddin Mohammad Ashraf, Shaik Sufiyan |\n")

    full_md = "".join(md)
    with open(OUT_MD_PATH, "w", encoding="utf-8") as f:
        f.write(full_md)
    print(f"[SUCCESS] Markdown artifact saved to {OUT_MD_PATH} (Length: {len(full_md)} chars)")

if __name__ == "__main__":
    main()
