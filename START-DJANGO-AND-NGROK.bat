@echo off
echo ========================================
echo Starting Django Server and Ngrok
echo ========================================
echo.

REM Start Django server in a new window
echo Starting Django server on port 8000...
start "Django Server" cmd /k "python manage.py runserver 8000"

REM Wait a moment for Django to start
timeout /t 3 /nobreak >nul

REM Start ngrok
echo.
echo Starting ngrok...
call START-NGROK.bat

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo IMPORTANT: Copy the HTTPS URL from the ngrok window
echo (It will look like: https://abc123.ngrok-free.app)
echo.
echo Next steps:
echo 1. Copy the ngrok HTTPS URL
echo 2. Add it to Google OAuth redirect URIs in Google Cloud Console
echo 3. Run: python update_site_for_ngrok.py
echo.
pause

