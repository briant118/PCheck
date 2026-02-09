# Start PCheck (Daphne) for use behind Nginx - listening on 127.0.0.1:8000 only
Write-Host "Starting PCheck (Daphne) for use behind Nginx..." -ForegroundColor Green
Set-Location $PSScriptRoot | Out-Null; Set-Location ..
if (Test-Path ".\venv\Scripts\Activate.ps1") { .\venv\Scripts\Activate.ps1 }
$env:DJANGO_SETTINGS_MODULE = "PCheckMain.settings"
python -m daphne -b 127.0.0.1 -p 8000 PCheckMain.asgi:application
