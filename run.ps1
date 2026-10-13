# Information Security Awareness Measurement System
# PowerShell Launcher Script

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Information Security Awareness Measurement System" -ForegroundColor White
Write-Host "  Measuring Information Security Behaviour Using Questionnaire Assessment" -ForegroundColor Gray
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
try {
    $pythonCmd = Get-Command python -ErrorAction Stop
    $pyVersion = (& python --version 2>&1)
    Write-Host "[1/5] Python installation detected: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://www.python.org/ and check 'Add to PATH'." -ForegroundColor Yellow
    Read-Host "Press Enter to exit..."
    exit 1
}

# 2. Virtual Environment
$venvPath = Join-Path $ScriptDir "venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$venvPip = Join-Path $venvPath "Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "[2/5] Creating Python virtual environment (venv)..." -ForegroundColor Yellow
    & python -m venv venv
    Write-Host "      Virtual environment created successfully." -ForegroundColor Green
} else {
    Write-Host "[2/5] Virtual environment already exists." -ForegroundColor Green
}

# 3. Install requirements
Write-Host "[3/5] Checking and installing dependencies from requirements.txt..." -ForegroundColor Yellow
& $venvPip install -r (Join-Path $ScriptDir "requirements.txt") --quiet
Write-Host "      Dependencies verified." -ForegroundColor Green

# 4. Initialize Database
Write-Host "[4/5] Initializing SQLite database schema and questions..." -ForegroundColor Yellow
& $venvPython -c "from models.database import init_db; init_db()"
Write-Host "      Database is ready." -ForegroundColor Green

# 5. Launch Application
Write-Host "[5/5] Starting Flask application..." -ForegroundColor Green
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Server URL: http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host "  Press CTRL+C in this terminal window to stop the server." -ForegroundColor Gray
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

try {
    Start-Process "http://127.0.0.1:5000"
} catch {
    # Non-fatal if browser cannot be launched automatically
}

& $venvPython (Join-Path $ScriptDir "app.py")
