# Setup Auto-Start for PC Notification Monitor
# This script creates a Windows Task Scheduler task to auto-start the notification page at login

param(
    [Parameter()][string]$ServerUrl = ""
)

$scriptPath = Join-Path $PSScriptRoot "START-PC-NOTIFICATIONS.ps1"
$taskName = "PCNotificationMonitor"

Write-Host "Setting up auto-start for PC Notification Monitor..." -ForegroundColor Cyan
Write-Host ""

# Check if script exists
if (-not (Test-Path $scriptPath)) {
    Write-Host "❌ Error: START-PC-NOTIFICATIONS.ps1 not found!" -ForegroundColor Red
    Write-Host "   Expected at: $scriptPath" -ForegroundColor Yellow
    exit 1
}

# Build PowerShell command
$psCommand = "& '$scriptPath'"
if ($ServerUrl) {
    $psCommand += " -ServerUrl '$ServerUrl'"
}

# Create Task Scheduler action
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -Command $psCommand"

# Create trigger (at logon)
$trigger = New-ScheduledTaskTrigger -AtLogOn

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Register the task
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Auto-start PC Notification Monitor at Windows login"
    Write-Host "✅ Auto-start task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Name: $taskName" -ForegroundColor White
    Write-Host "Trigger: At Windows Logon" -ForegroundColor White
    Write-Host "Script: $scriptPath" -ForegroundColor White
    Write-Host ""
    Write-Host "The notification page will now open automatically when you log in to Windows." -ForegroundColor Green
    Write-Host ""
    Write-Host "To test it now, run:" -ForegroundColor Yellow
    Write-Host "  .\START-PC-NOTIFICATIONS.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "To remove auto-start, run:" -ForegroundColor Yellow
    Write-Host "  Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false" -ForegroundColor White
} catch {
    Write-Host "❌ Error creating task: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "You may need to run PowerShell as Administrator." -ForegroundColor Yellow
    exit 1
}

