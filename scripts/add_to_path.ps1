# Script to add ZETA CLI to PATH on Windows
# Run as Administrator for system-wide PATH, or run normally for user PATH

Write-Host "ZETA CLI PATH Setup" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""

# Get Python Scripts directory
Write-Host "Finding Python Scripts directory..." -ForegroundColor Yellow
$pythonPath = python -m site --user-base 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Could not find Python installation" -ForegroundColor Red
    exit 1
}

$scriptsPath = Join-Path $pythonPath "Scripts"
Write-Host "Found: $scriptsPath" -ForegroundColor Green

# Check if directory exists
if (-not (Test-Path $scriptsPath)) {
    Write-Host "Warning: Scripts directory does not exist: $scriptsPath" -ForegroundColor Yellow
    Write-Host "ZETA CLI may not be installed correctly." -ForegroundColor Yellow
    exit 1
}

# Check if zeta.exe exists
$zetaExe = Join-Path $scriptsPath "zeta.exe"
if (-not (Test-Path $zetaExe)) {
    Write-Host "Warning: zeta.exe not found in $scriptsPath" -ForegroundColor Yellow
    Write-Host "This is normal on Windows - use 'python -m zeta' instead" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Recommended usage:" -ForegroundColor Green
    Write-Host "  python -m zeta --version" -ForegroundColor White
    Write-Host "  python -m zeta run 'your task'" -ForegroundColor White
    exit 0
}

# Get current PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

# Check if already in PATH
if ($currentPath -like "*$scriptsPath*") {
    Write-Host "✓ Scripts directory is already in PATH" -ForegroundColor Green
    Write-Host ""
    Write-Host "If 'zeta' command still doesn't work, restart PowerShell." -ForegroundColor Yellow
    exit 0
}

# Add to PATH
Write-Host "Adding to user PATH..." -ForegroundColor Yellow
$newPath = $currentPath + ";$scriptsPath"
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")

Write-Host "✓ Added to PATH successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Please restart PowerShell for changes to take effect." -ForegroundColor Yellow
Write-Host ""
Write-Host "After restarting, test with:" -ForegroundColor Cyan
Write-Host "  zeta --version" -ForegroundColor White
Write-Host ""
Write-Host "Alternatively, use (works immediately):" -ForegroundColor Cyan
Write-Host "  python -m zeta --version" -ForegroundColor White

