# Run session warnings checker
# This can run in a separate PowerShell window while the server is running

param(
    [Parameter()][int]$IntervalSeconds = 30,
    [Parameter()][switch]$Loop = $false
)

Set-Location $PSScriptRoot

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "Warning: Virtual environment not found. Make sure dependencies are installed." -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Session Warnings Checker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($Loop) {
    Write-Host "Running in loop mode (every $IntervalSeconds seconds)" -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    
    while ($true) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "[$timestamp] Checking for session warnings..." -ForegroundColor Green
        python manage.py check_session_warnings
        Write-Host ""
        Write-Host "Waiting $IntervalSeconds seconds before next check..." -ForegroundColor Gray
        Start-Sleep -Seconds $IntervalSeconds
    }
} else {
    Write-Host "Running once..." -ForegroundColor Yellow
    Write-Host ""
    python manage.py check_session_warnings
    Write-Host ""
    Write-Host "Done. Run with -Loop to run continuously." -ForegroundColor Gray
}

