# Enable ICMP (Ping) on Windows Firewall
# Run this script as Administrator on the User PC

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Enabling ICMP (Ping) on Windows Firewall" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Enabling ICMP Echo Request (Inbound)..." -ForegroundColor Green
netsh advfirewall firewall add rule name="ICMP Allow incoming V4 echo request" protocol=icmpv4:8,any dir=in action=allow

Write-Host ""
Write-Host "Enabling ICMP Echo Request (Outbound)..." -ForegroundColor Green
netsh advfirewall firewall add rule name="ICMP Allow outgoing V4 echo request" protocol=icmpv4:8,any dir=out action=allow

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ping has been enabled!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now ping this PC from other devices." -ForegroundColor Yellow
Write-Host ""
pause


