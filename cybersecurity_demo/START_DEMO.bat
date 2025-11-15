@echo off
echo ========================================
echo  Advance Agent for Cybersecurity Demo
echo ========================================
echo.

REM ตรวจสอบ Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python found!
echo.

REM ติดตั้ง dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed!
echo.

REM สร้างโฟลเดอร์ที่จำเป็น
if not exist "uploads" mkdir uploads
if not exist "data" mkdir data

echo ========================================
echo  Starting Demo Server...
echo ========================================
echo.
echo Dashboard:       http://localhost:5001
echo Knowledge Base:  http://localhost:5001/knowledge
echo Logs:            http://localhost:5001/logs
echo Agents:          http://localhost:5001/agents
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM รันแอป
python app.py

pause
