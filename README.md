@echo off
REM ==========================================
REM Arlo Camera System - Quick Start Script
REM For Windows
REM ==========================================

echo.
echo 🎥 Arlo Camera Management System - Setup
echo ==========================================
echo.

REM Check Python
echo ✓ Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python is not installed!
    echo   Install from: https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do (
    echo   Found: %%i
)

REM Check Node.js
echo ✓ Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Node.js is not installed!
    echo   Install from: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do (
    echo   Found: Node.js %%i
)

echo.
echo Setting up Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Checking for .env file...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo ✓ Created .env file from template
        echo   ⚠️  Edit .env with your credentials before running!
    ) else (
        echo ✗ .env.example not found!
        pause
        exit /b 1
    )
) else (
    echo ✓ .env file already exists
)

echo.
echo Installing Node.js dependencies...
call npm install

echo.
echo ✓ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your credentials:
echo    - Open .env in Notepad and fill in values
echo.
echo 2. Start the backend server (Command Prompt 1):
echo    venv\Scripts\activate.bat
echo    python arlo_backend.py
echo.
echo 3. Start the frontend (Command Prompt 2):
echo    npm start
echo.
echo 4. Open dashboard: http://localhost:3000
echo.
echo For detailed setup: Open SETUP_GUIDE.md
echo.
pause
