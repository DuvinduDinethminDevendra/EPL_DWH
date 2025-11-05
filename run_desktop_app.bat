@echo off
REM EPL DWH Desktop Application Launcher (Windows)
REM This script starts the PyQt6 desktop application

cls
echo.
echo ========================================
echo EPL Data Warehouse - Desktop Dashboard
echo ========================================
echo.

REM Check if .venv exists
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found
    echo Please run: python -m venv .venv
    echo Then: .\.venv\Scripts\activate.ps1
    pause
    exit /b 1
)

REM Activate virtual environment
call .\.venv\Scripts\activate.bat

REM Check if PyQt6 is installed
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing PyQt6...
    pip install PyQt6==6.6.1 PyQt6-Charts==6.6.1
)

REM Check if MySQL connection works
echo.
echo Checking database connection...
python -m src.etl.main --test-db >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Could not connect to database
    echo Make sure MySQL is running: docker-compose up -d
    echo.
    pause
)

REM Start the application
echo.
echo Starting application...
echo.
python desktop_app.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo Check error messages above
    pause
)

pause
