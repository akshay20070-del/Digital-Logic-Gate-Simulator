@echo off
title Smart Accident Detection System
echo ========================================================
echo   Launching Smart Accident Detection System (Python)
echo   Electronics & Communication Engineering Mini-Project
echo ========================================================
echo.
cd /d "%~dp0\software"
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while launching the application.
    pause
)
