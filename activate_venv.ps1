# PowerShell script to activate virtual environment
# This script sets the execution policy and activates the venv

# Set execution policy for current process (doesn't require admin)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# Activate the virtual environment
& .\venv\Scripts\Activate.ps1

Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host "Python path: $(python -c 'import sys; print(sys.executable)')" -ForegroundColor Cyan

