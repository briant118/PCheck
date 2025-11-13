# Start PC Notification Monitor
# This script automatically opens the PC notification page in fullscreen/kiosk mode
# It auto-detects the server URL or uses a config file

param(
    [Parameter()][string]$ServerUrl = "",
    [Parameter()][string]$PcName = $env:COMPUTERNAME,
    [Parameter()][switch]$NoKiosk = $false
)

# Function to detect server IP from network interfaces
function Get-ServerUrl {
    # First, try reading from config file
    $configFile = Join-Path $PSScriptRoot "pc-notification-config.txt"
    if (Test-Path $configFile) {
        $config = Get-Content $configFile -Raw
        if ($config -match "SERVER_URL=(.+)") {
            $url = $matches[1].Trim()
            Write-Host "Found server URL in config file: $url" -ForegroundColor Green
            return $url
        }
    }
    
    # Try to auto-detect server IP from network adapters
    Write-Host "Auto-detecting server IP..." -ForegroundColor Yellow
    try {
        $adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
            $_.IPAddress -notlike "127.*" -and 
            $_.IPAddress -notlike "169.254.*" 
        } | Sort-Object -Property IPAddress
        
        foreach ($adapter in $adapters) {
            $ip = $adapter.IPAddress
            $baseUrl = "http://$ip`:8000"
            
            # Test if server is reachable
            try {
                $response = Invoke-WebRequest -Uri "$baseUrl/pc-notification/" -Method Head -TimeoutSec 2 -ErrorAction Stop
                Write-Host "Found server at: $baseUrl" -ForegroundColor Green
                return $baseUrl
            } catch {
                # Try next IP
                continue
            }
        }
    } catch {
        Write-Host "Could not auto-detect server IP" -ForegroundColor Yellow
    }
    
    # Try common server IPs
    $commonIPs = @("192.168.137.238", "192.168.1.100", "192.168.0.100", "10.0.0.100")
    foreach ($ip in $commonIPs) {
        $baseUrl = "http://$ip`:8000"
        try {
            $response = Invoke-WebRequest -Uri "$baseUrl/pc-notification/" -Method Head -TimeoutSec 2 -ErrorAction Stop
            Write-Host "Found server at: $baseUrl" -ForegroundColor Green
            return $baseUrl
        } catch {
            continue
        }
    }
    
    # Fallback to localhost
    Write-Host "Using default: http://127.0.0.1:8000" -ForegroundColor Yellow
    return "http://127.0.0.1:8000"
}

# Get server URL
if ([string]::IsNullOrEmpty($ServerUrl)) {
    $ServerUrl = Get-ServerUrl
}

$notificationUrl = "$ServerUrl/pc-notification/?pc_name=$PcName"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PC Notification Monitor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PC Name: $PcName" -ForegroundColor White
Write-Host "Server: $ServerUrl" -ForegroundColor White
Write-Host "URL: $notificationUrl" -ForegroundColor White
Write-Host ""

# Wait a moment for any previous instances to close
Start-Sleep -Seconds 1

# Try Chrome first (most reliable)
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (Test-Path $chromePath) {
    Write-Host "Opening in Chrome..." -ForegroundColor Green
    if ($NoKiosk) {
        Start-Process $chromePath -ArgumentList "--new-window", $notificationUrl
    } else {
        # Kiosk mode: fullscreen, no UI
        Start-Process $chromePath -ArgumentList "--kiosk", "--app=$notificationUrl", "--disable-infobars", "--noerrdialogs"
    }
    Write-Host "✅ Chrome opened successfully!" -ForegroundColor Green
    exit 0
}

# Try Edge
$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (Test-Path $edgePath) {
    Write-Host "Opening in Edge..." -ForegroundColor Green
    if ($NoKiosk) {
        Start-Process $edgePath -ArgumentList "--new-window", $notificationUrl
    } else {
        Start-Process $edgePath -ArgumentList "--kiosk", "--app=$notificationUrl", "--disable-infobars", "--noerrdialogs"
    }
    Write-Host "✅ Edge opened successfully!" -ForegroundColor Green
    exit 0
}

# Fallback to default browser
Write-Host "Opening in default browser..." -ForegroundColor Yellow
try {
    Start-Process $notificationUrl
    Write-Host "✅ Browser opened successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error opening browser: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "The notification page is now open." -ForegroundColor Green
Write-Host "It will automatically show a warning when 5 minutes are left." -ForegroundColor Green
Write-Host ""


