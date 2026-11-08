@echo off
echo ============================================================
echo   flood-ews 6-Node Real-Time Telemetry Simulator (Tirupati)
echo ============================================================
echo.
echo Simulating all 6 drainage nodes across Tirupati:
echo  - drain-01: Kapilatheertham Nallah (Alipiri)
echo  - drain-02: Leela Mahal Culvert (Korlagunta)
echo  - drain-03: Railway Underbridge (West) (Tata Nagar)
echo  - drain-04: Korlagunta Storm Canal (Korlagunta)
echo  - drain-05: Alipiri Footpath Channel (Alipiri)
echo  - drain-06: Tiruchanur Swarnamukhi Causeway (Tiruchanur)
echo.
echo Streaming live telemetry to broker.hivemq.com:1883...
echo Press Ctrl+C anytime to stop simulation.
echo.

set PYTHONPATH=.
backend\.venv\Scripts\python.exe scripts\simulate.py --scenario normal --duration 0
pause
