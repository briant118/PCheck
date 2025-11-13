@echo off
REM Auto-start PC Notification Monitor
REM This script runs continuously and automatically opens the notification page
REM when a session is about to end (5 minutes left)
REM Run this script at Windows startup or via Task Scheduler

set SERVER_URL=http://192.168.137.238:8000
set PC_NAME=%COMPUTERNAME%
set CHECK_INTERVAL=30

echo ========================================
echo Auto PC Notification Monitor
echo ========================================
echo PC Name: %PC_NAME%
echo Server: %SERVER_URL%
echo Check Interval: %CHECK_INTERVAL% seconds
echo.

cd /d %~dp0

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Run PowerShell script
powershell.exe -ExecutionPolicy Bypass -File "%~dp0AUTO-START-PC-NOTIFICATIONS.ps1" -ServerUrl "%SERVER_URL%" -PcName "%PC_NAME%" -CheckInterval %CHECK_INTERVAL%

pause

