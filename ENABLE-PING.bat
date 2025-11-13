@echo off
REM Enable ICMP (Ping) on Windows Firewall
REM Run this script as Administrator on the User PC

echo ========================================
echo Enabling ICMP (Ping) on Windows Firewall
echo ========================================
echo.
echo This script will allow incoming ping requests.
echo You need to run this as Administrator!
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Removing existing ICMP rules (if any)...
netsh advfirewall firewall delete rule name="ICMP Allow incoming V4 echo request" >nul 2>&1
netsh advfirewall firewall delete rule name="ICMP Allow outgoing V4 echo request" >nul 2>&1

echo.
echo Enabling ICMP Echo Request (Inbound)...
netsh advfirewall firewall add rule name="ICMP Allow incoming V4 echo request" protocol=icmpv4:8,any dir=in action=allow

echo.
echo Enabling ICMP Echo Request (Outbound)...
netsh advfirewall firewall add rule name="ICMP Allow outgoing V4 echo request" protocol=icmpv4:8,any dir=out action=allow

echo.
echo Enabling ICMP for all profiles (Domain, Private, Public)...
netsh advfirewall firewall set rule name="ICMP Allow incoming V4 echo request" new enable=yes profile=domain,private,public
netsh advfirewall firewall set rule name="ICMP Allow outgoing V4 echo request" new enable=yes profile=domain,private,public

echo.
echo ========================================
echo Ping has been enabled!
echo ========================================
echo.
echo Testing ping connectivity...
ping -n 1 127.0.0.1 >nul 2>&1
if %errorLevel% equ 0 (
    echo Local ping test: SUCCESS
) else (
    echo Local ping test: FAILED
)

echo.
echo You can now ping this PC from other devices.
echo.
echo IMPORTANT: If ping still doesn't work, check:
echo 1. Windows Firewall is not blocking ICMP
echo 2. Antivirus software is not blocking ICMP
echo 3. Network adapter firewall settings
echo.
pause

