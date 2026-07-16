@echo off
REM ===================================================================
REM  Argus AI - one-click launcher (Windows)
REM  Double-click this file, or run:  run.bat
REM
REM  It uses the project's own virtual environment, so the AI/camera
REM  libraries are always found. (Running plain "python" instead can
REM  use the wrong Python and silently disable the webcam.)
REM ===================================================================
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo.
        echo ERROR: Could not create the virtual environment.
        echo Make sure Python 3.10 - 3.12 is installed and on your PATH.
        pause
        exit /b 1
    )
)

.venv\Scripts\python.exe -c "import cv2, mediapipe" >nul 2>&1
if errorlevel 1 (
    echo [2/3] Installing dependencies ^(first run only, a few minutes^)...
    .venv\Scripts\python.exe -m pip install --upgrade pip >nul
    .venv\Scripts\python.exe -m pip install -r requirements-ml.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Install failed. You most likely have Python 3.13+,
        echo which MediaPipe does not support yet. Install Python 3.12.
        pause
        exit /b 1
    )
)

echo [3/3] Starting Argus AI...
echo.
echo    Open your browser at:  http://127.0.0.1:5000
echo    Login: demo@argus.ai / demo123   (admin@argus.ai / admin123)
echo.
echo    Press CTRL+C here to stop the server.
echo.
.venv\Scripts\python.exe -m backend.api_server
pause
