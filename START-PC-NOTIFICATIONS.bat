@echo off
REM Simple wrapper to run the PowerShell script
REM Just double-click this file to start the PC Notification Monitor

powershell.exe -ExecutionPolicy Bypass -File "%~dp0START-PC-NOTIFICATIONS.ps1"

pause
