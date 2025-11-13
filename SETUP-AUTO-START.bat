@echo off
REM Setup Auto-Start PC Notification Monitor
REM This creates a Windows Task Scheduler task to run the notification monitor at startup

echo ========================================
echo Setting up Auto-Start PC Notification Monitor
echo ========================================
echo.
echo This will create a Windows Task Scheduler task that:
echo - Runs at Windows startup
echo - Automatically opens the notification page when 5 minutes are left
echo - Keeps the notification page running
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

set SCRIPT_PATH=%~dp0AUTO-START-PC-NOTIFICATIONS.ps1
set TASK_NAME=PCNotificationMonitor

echo Creating scheduled task...
echo Task Name: %TASK_NAME%
echo Script Path: %SCRIPT_PATH%
echo.

REM Delete existing task if it exists
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

REM Create new task
schtasks /Create /TN "%TASK_NAME%" /TR "powershell.exe -ExecutionPolicy Bypass -File \"%SCRIPT_PATH%\"" /SC ONSTART /RU SYSTEM /RL HIGHEST /F

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo Task created successfully!
    echo ========================================
    echo.
    echo The PC Notification Monitor will now:
    echo - Start automatically when Windows boots
    echo - Open the notification page when 5 minutes are left
    echo - Keep the notification page running
    echo.
    echo To remove the task later, run:
    echo   schtasks /Delete /TN "%TASK_NAME%"
    echo.
) else (
    echo.
    echo ERROR: Failed to create task
    echo.
)

pause

