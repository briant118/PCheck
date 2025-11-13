@echo off
REM Run session warnings checker
REM This can run in a separate window while the server is running

echo ========================================
echo Session Warnings Checker
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
echo This will check for bookings ending in 5 minutes
echo and send WebSocket warnings to connected PCs.
echo.
echo Press Ctrl+C to stop
echo.

python manage.py check_session_warnings

pause

