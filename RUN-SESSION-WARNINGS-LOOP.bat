@echo off
REM Run session warnings checker in a loop (every 30 seconds)
REM This can run in a separate window while the server is running

echo ========================================
echo Session Warnings Checker (Loop Mode)
echo ========================================
echo.

cd /d %~dp0

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found. Make sure dependencies are installed.
)

echo.
echo This will check for bookings every 30 seconds
echo and send WebSocket warnings to connected PCs.
echo.
echo Press Ctrl+C to stop
echo.

:loop
echo [%date% %time%] Checking for session warnings...
python manage.py check_session_warnings
echo.
echo Waiting 30 seconds before next check...
timeout /t 30 /nobreak >nul
goto loop

