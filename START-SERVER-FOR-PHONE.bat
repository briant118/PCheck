@echo off
echo ========================================
echo   PCheck Server - Mobile Access Setup
echo ========================================
echo.

echo Finding your local IP address...
echo.

REM Get the main network IP (not virtual adapters)
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set ip=%%a
    set ip=!ip: =!
    REM Skip virtual adapter IPs (usually 192.168.56.x or 192.168.137.x)
    echo !ip! | findstr /v "192.168.56 192.168.137" >nul
    if !errorlevel! equ 0 (
        echo Your server will be accessible at: http://!ip!:8000
        echo.
    )
)

echo All IP addresses on this computer:
ipconfig | findstr /i "IPv4"
echo.

echo ========================================
echo   Instructions:
echo ========================================
echo 1. Make sure your phone is on the SAME WiFi network
echo 2. On your phone, open a browser and go to:
echo    http://192.168.100.20:8000
echo    (or use one of the IPs shown above)http://192.168.100.20:8000/reservation-approval/183/

echo.   
echo 3. If it doesn't work, check Windows Firewall:
echo    - Allow Python/Daphne through firewall
echo    - Or temporarily disable firewall for testing
echo.
echo ========================================
echo   Starting server...
echo ========================================
echo.http://192.168.100.20:8000/reservation-approval/212/


cd /d %~dp0
set DJANGO_SETTINGS_MODULE=PCheckMain.settings
python -m daphne -b 0.0.0.0 -p 8000 PCheckMain.asgi:application

pause

