@echo off
REM Simple Auto-Start: Just open the notification page at Windows startup
REM The page will automatically go fullscreen when 5 minutes are left

set SERVER_URL=http://192.168.137.238:8000
set PC_NAME=%COMPUTERNAME%

REM Open in Chrome kiosk mode (fullscreen, stays open)
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk --app=%SERVER_URL%/pc-notification/?pc_name=%PC_NAME%

REM Alternative: Open in Edge kiosk mode
REM start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --kiosk --app=%SERVER_URL%/pc-notification/?pc_name=%PC_NAME%

REM Alternative: Open in default browser (not fullscreen, but will go fullscreen when warning arrives)
REM start "" %SERVER_URL%/pc-notification/?pc_name=%PC_NAME%

echo PC Notification Monitor started for %PC_NAME%
echo The page will automatically go fullscreen when 5 minutes are left.

