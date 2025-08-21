@echo off
echo Android App Generator
echo ===================
echo.
echo Starting application...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show gpt4all >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Run the application
echo Starting Android App Generator...
python main.py

REM If the application exits with an error, pause to show the error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)