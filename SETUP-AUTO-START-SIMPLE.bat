@echo off
REM Setup Simple Auto-Start PC Notification Monitor
REM This creates a Windows Task Scheduler task to open the notification page at startup

echo ========================================
echo Setting up Auto-Start PC Notification Monitor
echo ========================================
echo.
echo This will create a Windows Task Scheduler task that:
echo - Opens the notification page when Windows starts
echo - Page stays open and automatically goes fullscreen when 5 minutes are left
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

set SCRIPT_PATH=%~dp0AUTO-START-SIMPLE.bat
set TASK_NAME=PCNotificationMonitor

echo Creating scheduled task...
echo Task Name: %TASK_NAME%
echo Script Path: %SCRIPT_PATH%
echo.

REM Delete existing task if it exists
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

REM Create new task (runs at startup, runs as current user)
schtasks /Create /TN "%TASK_NAME%" /TR "\"%SCRIPT_PATH%\"" /SC ONSTART /F

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo Task created successfully!
    echo ========================================
    echo.
    echo The PC Notification Monitor will now:
    echo - Open automatically when Windows boots
    echo - Stay open in the background
    echo - Automatically go fullscreen when 5 minutes are left
    echo.
    echo To test: Restart your computer or run the task manually:
    echo   schtasks /Run /TN "%TASK_NAME%"
    echo.
    echo To remove the task later:
    echo   schtasks /Delete /TN "%TASK_NAME%"
    echo.
) else (
    echo.
    echo ERROR: Failed to create task
    echo.
)

pause

