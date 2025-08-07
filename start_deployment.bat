@echo off
echo ======================================
echo    UnderLand Bot - Cloud Deployment
echo ======================================
echo.
echo Starting deployment-optimized version...
echo Features: Games, Social, Utils, Moderation
echo No AI/Music dependencies for cloud hosting
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if requirements are installed
pip show discord.py >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements_deployment.txt
)

REM Set environment variable for deployment mode
set ENVIRONMENT=production

REM Start the bot
echo Starting bot...
python run_deployment.py

pause
