# Download and set up Nginx for Windows in deploy/nginx, with PCheck config.
# Run from PCheck project root: .\deploy\setup_nginx_windows.ps1

$ErrorActionPreference = "Stop"
$DeployDir = $PSScriptRoot
$NginxZipUrl = "https://nginx.org/download/nginx-1.28.2.zip"
$NginxZip = Join-Path $DeployDir "nginx-1.28.2.zip"
$NginxDir = Join-Path $DeployDir "nginx"

if (Test-Path $NginxDir) {
    Write-Host "Nginx already exists at $NginxDir. Remove it first to re-run setup." -ForegroundColor Yellow
    exit 0
}

Write-Host "Downloading Nginx (stable)..." -ForegroundColor Green
Invoke-WebRequest -Uri $NginxZipUrl -OutFile $NginxZip -UseBasicParsing

Write-Host "Extracting..." -ForegroundColor Green
Expand-Archive -Path $NginxZip -DestinationPath $DeployDir -Force
Remove-Item $NginxZip -Force

$Extracted = Get-ChildItem $DeployDir -Directory | Where-Object { $_.Name -match "nginx-" } | Select-Object -First 1
if (-not $Extracted) {
    Write-Host "Unexpected zip structure. Check deploy folder." -ForegroundColor Red
    exit 1
}
Rename-Item $Extracted.FullName $NginxDir

# Create sites folder and copy PCheck config
$SitesDir = Join-Path $NginxDir "conf\sites"
New-Item -ItemType Directory -Path $SitesDir -Force | Out-Null
Copy-Item (Join-Path $DeployDir "nginx-pcheck.conf") (Join-Path $SitesDir "pcheck.conf") -Force

# Add include to nginx.conf (inside http block, before the closing })
$NginxConf = Join-Path $NginxDir "conf\nginx.conf"
$lines = Get-Content $NginxConf -Raw
if ($lines -notmatch "include\s+sites") {
    # Insert before the last closing brace of the file (end of http block)
    $lines = $lines -replace "(\s*)(}\s*)$", "`$1    include sites/pcheck.conf;`n`$1`$2"
    Set-Content $NginxConf $lines -NoNewline
    Write-Host "Added include sites/pcheck.conf to nginx.conf" -ForegroundColor Green
} else {
    Write-Host "nginx.conf already includes sites config." -ForegroundColor Gray
}

Write-Host "Done. Nginx is at: $NginxDir" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit $SitesDir\pcheck.conf - set your domain and paths."
Write-Host "  2. Start Daphne (behind Nginx): .\deploy\start_daphne_behind_nginx.bat"
Write-Host "  3. Start Nginx: $NginxDir\nginx.exe"
Write-Host "  4. Get SSL (e.g. win-acme) and add domain to .env. See deploy\README.md"
