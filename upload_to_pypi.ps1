# ZETA PyPI Upload Script
# This script handles the final upload to PyPI

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ZETA PyPI Upload Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .pypirc exists
$pypircPath = "$env:USERPROFILE\.pypirc"
if (-not (Test-Path $pypircPath)) {
    Write-Host "ERROR: .pypirc file not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create it first:" -ForegroundColor Yellow
    Write-Host "1. Copy .pypirc.template to $pypircPath" -ForegroundColor Yellow
    Write-Host "2. Edit it and add your PyPI API token" -ForegroundColor Yellow
    Write-Host "3. Run this script again" -ForegroundColor Yellow
    exit 1
}

# Check if dist folder exists
if (-not (Test-Path "dist")) {
    Write-Host "ERROR: dist folder not found!" -ForegroundColor Red
    Write-Host "Please run: python -m build" -ForegroundColor Yellow
    exit 1
}

# List files to upload
Write-Host "Files to upload:" -ForegroundColor Green
Get-ChildItem dist\* | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor Gray
}
Write-Host ""

# Ask for confirmation
$confirm = Read-Host "Ready to upload to PyPI? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Upload cancelled." -ForegroundColor Yellow
    exit 0
}

# Upload to PyPI
Write-Host ""
Write-Host "Uploading to PyPI..." -ForegroundColor Cyan
python -m twine upload dist/*

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Package uploaded to PyPI!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your package will be available at:" -ForegroundColor Yellow
    Write-Host "https://pypi.org/project/zeta-cli/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Test installation:" -ForegroundColor Yellow
    Write-Host "  pip install zeta-cli" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ERROR: Upload failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Check your API token in .pypirc" -ForegroundColor Gray
    Write-Host "2. Verify internet connection" -ForegroundColor Gray
    Write-Host "3. Check if package name is available" -ForegroundColor Gray
    Write-Host ""
}

