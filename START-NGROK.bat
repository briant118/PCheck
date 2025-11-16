@echo off
echo ========================================
echo Starting Ngrok for PCheck Application
echo ========================================
echo.
echo Make sure your Django server is running on port 8000!
echo.
pause

REM Check if ngrok is in the current directory
if exist "ngrok.exe" (
    echo Found ngrok.exe in current directory
    start "Ngrok" cmd /k "ngrok.exe http 8000"
) else (
    REM Try to use ngrok from PATH
    where ngrok >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Using ngrok from PATH
        start "Ngrok" cmd /k "ngrok http 8000"
    ) else (
        echo ERROR: ngrok.exe not found!
        echo.
        echo Please either:
        echo 1. Place ngrok.exe in this directory, OR
        echo 2. Add ngrok to your PATH environment variable
        echo.
        echo Download ngrok from: https://ngrok.com/download
        pause
        exit /b 1
    )
)

echo.
echo Ngrok is starting in a new window...
echo.
echo IMPORTANT: Copy the HTTPS URL from the ngrok window
echo (It will look like: https://abc123.ngrok-free.app)
echo.
echo Then:
echo 1. Add it to Google OAuth redirect URIs in Google Cloud Console
echo 2. Run: python update_site_for_ngrok.py
echo.
pause

