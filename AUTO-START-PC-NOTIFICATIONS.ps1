# Auto-start PC Notification Monitor
# This script runs continuously and automatically opens the notification page
# when a session is about to end (5 minutes left)
# Run this script at Windows startup or via Task Scheduler

param(
    [Parameter()][string]$ServerUrl = "http://192.168.137.238:8000",
    [Parameter()][string]$PcName = $env:COMPUTERNAME,
    [Parameter()][int]$CheckInterval = 30  # Check every 30 seconds
)

$notificationUrl = "$ServerUrl/pc-notification/?pc_name=$PcName"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Auto PC Notification Monitor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PC Name: $PcName" -ForegroundColor Yellow
Write-Host "Server: $ServerUrl" -ForegroundColor Yellow
Write-Host "Check Interval: $CheckInterval seconds" -ForegroundColor Yellow
Write-Host ""

# Function to check if notification page is already open
function Is-NotificationPageOpen {
    $chromeProcesses = Get-Process -Name "chrome" -ErrorAction SilentlyContinue | Where-Object {
        $_.MainWindowTitle -like "*PC Session Monitor*" -or
        $_.CommandLine -like "*pc-notification*"
    }
    $edgeProcesses = Get-Process -Name "msedge" -ErrorAction SilentlyContinue | Where-Object {
        $_.MainWindowTitle -like "*PC Session Monitor*" -or
        $_.CommandLine -like "*pc-notification*"
    }
    return ($chromeProcesses.Count -gt 0) -or ($edgeProcesses.Count -gt 0)
}

# Function to open notification page
function Open-NotificationPage {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Opening notification page..." -ForegroundColor Green
    
    # Try Chrome first
    $chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    if (Test-Path $chromePath) {
        Start-Process $chromePath -ArgumentList "--kiosk", "--app=$notificationUrl" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        return $true
    }
    
    # Try Edge
    $edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if (Test-Path $edgePath) {
        Start-Process $edgePath -ArgumentList "--kiosk", "--app=$notificationUrl" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        return $true
    }
    
    # Fallback to default browser
    Start-Process $notificationUrl -ErrorAction SilentlyContinue
    return $true
}

# Function to check for active session via API
function Check-ActiveSession {
    try {
        $response = Invoke-RestMethod -Uri "$ServerUrl/ajax/get-my-active-booking/" -Method GET -ErrorAction SilentlyContinue
        if ($response -and $response.has_booking -eq $true) {
            # Parse end_time if available
            if ($response.end_time) {
                $endTime = [DateTime]::Parse($response.end_time)
                $now = Get-Date
                $timeLeft = $endTime - $now
                $minutesLeft = [math]::Floor($timeLeft.TotalMinutes)
                
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Active session found. $minutesLeft minutes remaining." -ForegroundColor Cyan
                
                # If 5 minutes or less, ensure notification page is open
                if ($minutesLeft -le 5 -and $minutesLeft -gt 0) {
                    if (-not (Is-NotificationPageOpen)) {
                        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ⚠️ 5 minutes or less remaining! Opening notification page..." -ForegroundColor Red
                        Open-NotificationPage
                    } else {
                        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Notification page already open." -ForegroundColor Green
                    }
                    return $true
                }
            }
            return $true
        }
        return $false
    } catch {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Error checking session: $($_.Exception.Message)" -ForegroundColor Yellow
        return $false
    }
}

# Main loop
Write-Host "Starting monitoring loop..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Open notification page immediately on startup
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Opening notification page on startup..." -ForegroundColor Green
Open-NotificationPage
Start-Sleep -Seconds 5

while ($true) {
    try {
        # Check for active session
        $hasSession = Check-ActiveSession
        
        if (-not $hasSession) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] No active session." -ForegroundColor Gray
        }
        
        # Also ensure notification page stays open (in case it was closed)
        if (-not (Is-NotificationPageOpen)) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Notification page closed. Reopening..." -ForegroundColor Yellow
            Open-NotificationPage
        }
        
    } catch {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Error in main loop: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds $CheckInterval
}

