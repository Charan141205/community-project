# ============================================================
# flood-ews 6-Node Real-Time Telemetry Simulator (PowerShell)
# ============================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  flood-ews 6-Node Real-Time Telemetry Simulator (Tirupati)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Simulating all 6 drainage nodes across Tirupati:" -ForegroundColor Green
Write-Host " - drain-01: Kapilatheertham Nallah (Alipiri)"
Write-Host " - drain-02: Leela Mahal Culvert (Korlagunta)"
Write-Host " - drain-03: Railway Underbridge (West) (Tata Nagar)"
Write-Host " - drain-04: Korlagunta Storm Canal (Korlagunta)"
Write-Host " - drain-05: Alipiri Footpath Channel (Alipiri)"
Write-Host " - drain-06: Tiruchanur Swarnamukhi Causeway (Tiruchanur)"
Write-Host ""
Write-Host "Streaming live telemetry to broker.hivemq.com:1883..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop simulation." -ForegroundColor Gray
Write-Host ""

$rootDir = $PSScriptRoot
if (-not $rootDir) { $rootDir = Get-Location }

$env:PYTHONPATH = $rootDir
& "$rootDir\backend\.venv\Scripts\python.exe" "$rootDir\scripts\simulate.py" --scenario normal --duration 0
