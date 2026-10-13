@echo off
setlocal enabledelayedexpansion

title Information Security Awareness Measurement System
cd /d "%~dp0"

echo ======================================================================
echo   Information Security Awareness Measurement System
echo   Measuring Information Security Behaviour Using Questionnaire Assessment
echo ======================================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not detected in your system PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    echo Ensure you check the box "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/5] Python installation detected.
python --version

:: 2. Create virtual environment if it doesn't exist
if not exist "venv\Scripts\activate.bat" (
    echo [2/5] Creating Python virtual environment (venv)...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo       Virtual environment created successfully.
) else (
    echo [2/5] Virtual environment already exists.
)

:: 3. Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

:: 4. Install requirements
echo [4/5] Checking and installing dependencies from requirements.txt...
pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Pip install returned non-zero status. Retrying with verbose output...
    pip install -r requirements.txt
)

:: 5. Initialize database
echo [5/5] Ensuring SQLite database and questionnaire schema are initialized...
python -c "from models.database import init_db; init_db()"

echo.
echo ======================================================================
echo   Starting Flask Web Server...
echo   Open your web browser at: http://127.0.0.1:5000
echo   Press CTRL+C in this terminal window to stop the server.
echo ======================================================================
echo.

:: Launch the default web browser after a brief delay in the background
start "" http://127.0.0.1:5000

:: Start Flask application
python app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] The application stopped unexpectedly.
    pause
)
