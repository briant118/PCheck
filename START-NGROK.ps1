# PowerShell script to start ngrok for PCheck Application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Ngrok for PCheck Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Make sure your Django server is running on port 8000!" -ForegroundColor Yellow
Write-Host ""

# Check if ngrok exists in current directory
if (Test-Path "ngrok.exe") {
    Write-Host "Found ngrok.exe in current directory" -ForegroundColor Green
    Start-Process "ngrok.exe" -ArgumentList "http", "8000" -NoNewWindow
} elseif (Get-Command ngrok -ErrorAction SilentlyContinue) {
    Write-Host "Using ngrok from PATH" -ForegroundColor Green
    Start-Process "ngrok" -ArgumentList "http", "8000" -NoNewWindow
} else {
    Write-Host "ERROR: ngrok not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please either:" -ForegroundColor Yellow
    Write-Host "1. Place ngrok.exe in this directory, OR" -ForegroundColor Yellow
    Write-Host "2. Add ngrok to your PATH environment variable" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Download ngrok from: https://ngrok.com/download" -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Ngrok is starting..." -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Copy the HTTPS URL from the ngrok output" -ForegroundColor Yellow
Write-Host "(It will look like: https://abc123.ngrok-free.app)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Then:" -ForegroundColor Cyan
Write-Host "1. Add it to Google OAuth redirect URIs in Google Cloud Console" -ForegroundColor Cyan
Write-Host "2. Run: python update_site_for_ngrok.py" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue"

