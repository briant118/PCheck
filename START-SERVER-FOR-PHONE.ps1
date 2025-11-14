Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PCheck Server - Mobile Access Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Finding your local IP address..." -ForegroundColor Yellow
Write-Host ""

# Get all IPv4 addresses
$ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" } | Select-Object -ExpandProperty IPAddress

Write-Host "Your server will be accessible at:" -ForegroundColor Green
foreach ($ip in $ipAddresses) {
    # Skip virtual adapter IPs
    if ($ip -notlike "192.168.56.*" -and $ip -notlike "192.168.137.*") {
        Write-Host "  http://$ip`:8000" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "All IP addresses on this computer:" -ForegroundColor Yellow
Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" } | Format-Table IPAddress, InterfaceAlias -AutoSize

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Instructions:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Make sure your phone is on the SAME WiFi network" -ForegroundColor White
Write-Host "2. On your phone, open a browser and go to:" -ForegroundColor White
Write-Host "   http://192.168.100.20:8000" -ForegroundColor Green
Write-Host "   (or use one of the IPs shown above)" -ForegroundColor White
Write-Host ""
Write-Host "3. If it doesn't work, check Windows Firewall:" -ForegroundColor White
Write-Host "   - Allow Python/Daphne through firewall" -ForegroundColor Yellow
Write-Host "   - Or temporarily disable firewall for testing" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting server..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot
$env:DJANGO_SETTINGS_MODULE = "PCheckMain.settings"
python -m daphne -b 0.0.0.0 -p 8000 PCheckMain.asgi:application

