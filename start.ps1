# ============================================================
# flood-ews Local Launcher Script (PowerShell)
# ============================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting flood-ews Local Services (FastAPI + Next.js)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = $PSScriptRoot
if (-not $rootDir) { $rootDir = Get-Location }

# 1. Start Backend in a background process / new window
Write-Host "[1/2] Launching Backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir'; `$env:PYTHONPATH='.'; & '$rootDir\backend\.venv\Scripts\python.exe' -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

# 2. Start Dashboard in a new window
Write-Host "[2/2] Launching Next.js Dashboard on http://localhost:3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir\dashboard'; npm run dev"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Services launched in separate windows!" -ForegroundColor Green
Write-Host "  - Community Public Portal: http://localhost:3000/public" -ForegroundColor Yellow
Write-Host "  - Operator Command Center: http://localhost:3000/ops" -ForegroundColor Yellow
Write-Host "  - FastAPI Documentation:  http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
