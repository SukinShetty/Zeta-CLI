# Upgrade ZETA CLI to latest version and fix PATH
# Run this script to upgrade and test ZETA CLI

Write-Host "Upgrading ZETA CLI..." -ForegroundColor Cyan
Write-Host ""

# Upgrade the package
pip install --upgrade --force-reinstall zeta-cli

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to upgrade ZETA CLI" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Checking installed version..." -ForegroundColor Yellow
$version = pip show zeta-cli | Select-String -Pattern "Version"
Write-Host $version -ForegroundColor Green

Write-Host ""
Write-Host "Testing zeta command..." -ForegroundColor Yellow

# Add Scripts to PATH for this session
$pythonBase = python -m site --user-base 2>&1
$scriptsPath = Join-Path (Split-Path $pythonBase -Parent) "Scripts"
$scriptsPath = Join-Path $scriptsPath ""

# Try alternative path
if (-not (Test-Path $scriptsPath)) {
    $scriptsPath = "$env:LOCALAPPDATA\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts"
}

$env:Path += ";$scriptsPath"

# Test the command
$result = zeta --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ SUCCESS! ZETA CLI is working!" -ForegroundColor Green
    Write-Host "Output: $result" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Close and reopen PowerShell for PATH changes to persist." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✗ Error testing zeta command:" -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
    Write-Host ""
    Write-Host "Try using: python -m zeta --version" -ForegroundColor Cyan
}

