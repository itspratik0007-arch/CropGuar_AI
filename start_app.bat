@echo off
title CropGuard AI Launcher
echo ===================================================
echo Starting CropGuard AI Fullstack Application...
echo ===================================================

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "CropGuard Backend" cmd /k "cd /d ""%ROOT_DIR%"" && call .\backend\venv\Scripts\activate.bat && set PYTHONPATH=backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Launching React Frontend on http://localhost:5173 ...
start "CropGuard Frontend" cmd /k "cd /d ""%ROOT_DIR%frontend"" && npm run dev -- --host 127.0.0.1"

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
