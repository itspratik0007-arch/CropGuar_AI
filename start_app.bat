@echo off
title CropGuard AI Launcher
echo ===================================================
echo Starting CropGuard AI Fullstack Application...
echo ===================================================

cd /d "%~dp0"

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "CropGuard Backend" cmd /k "call .\backend\venv\Scripts\activate.bat && set PYTHONPATH=backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting React Frontend on http://localhost:5173 ...
cd frontend
start "CropGuard Frontend" cmd /k "npm run dev -- --host 127.0.0.1"

echo.
echo Waiting for servers to initialize...
timeout /t 3 /nobreak >nul

echo Opening CropGuard AI in your browser...
start http://127.0.0.1:5173

echo.
echo ===================================================
echo CropGuard AI is running!
echo - Frontend: http://127.0.0.1:5173
echo - Backend API Docs: http://127.0.0.1:8000/docs
echo ===================================================
pause
