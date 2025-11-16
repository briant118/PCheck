# PowerShell script to configure ngrok with auth token

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuring Ngrok with Auth Token" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$authtoken = "35ZI7RgaYdaKYG5iTotWLwUPRre_i5vaQ7UVVkQFSGpGjWBB"

# Check if ngrok exists in current directory
if (Test-Path "ngrok.exe") {
    Write-Host "Found ngrok.exe in current directory" -ForegroundColor Green
    $ngrokPath = ".\ngrok.exe"
} elseif (Get-Command ngrok -ErrorAction SilentlyContinue) {
    Write-Host "Using ngrok from PATH" -ForegroundColor Green
    $ngrokPath = "ngrok"
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

# Configure ngrok
Write-Host "Configuring ngrok..." -ForegroundColor Yellow
$result = & $ngrokPath config add-authtoken $authtoken 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Ngrok configured successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now start ngrok using:" -ForegroundColor Cyan
    Write-Host "  .\START-NGROK.ps1" -ForegroundColor Cyan
    Write-Host "  or" -ForegroundColor Cyan
    Write-Host "  START-NGROK.bat" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ERROR: Failed to configure ngrok" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "1. Ngrok is installed correctly" -ForegroundColor Yellow
    Write-Host "2. You have internet connection" -ForegroundColor Yellow
    Write-Host "3. The authtoken is valid" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Error output:" -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to continue"

