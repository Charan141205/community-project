@echo off
echo ============================================================
echo   Starting flood-ews Local Services (FastAPI + Next.js)
echo ============================================================
echo.

:: Check for virtual environment
if not exist "backend\.venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    python -m venv backend\.venv
    call backend\.venv\Scripts\activate.bat
    pip install -r backend\requirements.txt
)

:: Check for node_modules
if not exist "dashboard\node_modules" (
    echo Installing Dashboard dependencies...
    cd dashboard
    call npm install
    cd ..
)

echo Starting Backend API on http://localhost:8000...
start "flood-ews Backend API" cmd /k "set PYTHONPATH=. && backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting Next.js Dashboard on http://localhost:3000...
start "flood-ews Dashboard" cmd /k "cd dashboard && npm run dev"

echo.
echo ============================================================
echo [SUCCESS] Both services are launching in separate windows!
echo - Public Community Portal: http://localhost:3000/public
echo - Operator Command Center: http://localhost:3000/ops
echo - Backend OpenAPI Docs:    http://localhost:8000/docs
echo ============================================================
echo.
pause
