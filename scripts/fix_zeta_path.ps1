# Fix ZETA CLI PATH on Windows
# This script adds the Python Scripts directory to your PATH

Write-Host "ZETA CLI PATH Fix" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host ""

# Find Python Scripts directory
Write-Host "Finding Python Scripts directory..." -ForegroundColor Yellow

$pythonBase = python -m site --user-base 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Could not find Python installation" -ForegroundColor Red
    exit 1
}

# Construct Scripts path
$scriptsPath = Join-Path (Split-Path $pythonBase -Parent) "Scripts"
$scriptsPath = Join-Path $scriptsPath ""

# Alternative method if above doesn't work
if (-not (Test-Path $scriptsPath)) {
    $scriptsPath = Join-Path $pythonBase "..\Python311\Scripts"
    $scriptsPath = $scriptsPath -replace '\\local-packages$', '\local-packages\Python311\Scripts'
}

# Try to find Scripts directory
$possiblePaths = @(
    "$env:LOCALAPPDATA\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts",
    "$env:APPDATA\Python\Python311\Scripts",
    "$env:LOCALAPPDATA\Programs\Python\Python311\Scripts"
)

$foundPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $zetaExe = Join-Path $path "zeta.exe"
        if (Test-Path $zetaExe) {
            $foundPath = $path
            break
        }
    }
}

# Use the found path or try constructing from user-base
if (-not $foundPath) {
    $pythonBase = python -m site --user-base 2>&1
    $foundPath = $pythonBase -replace 'local-packages$', 'local-packages\Python311\Scripts'
    
    if (-not (Test-Path $foundPath)) {
        # Try alternative construction
        $baseDir = Split-Path $pythonBase -Parent
        $foundPath = Join-Path $baseDir "Python311\Scripts"
    }
}

if (-not (Test-Path $foundPath)) {
    Write-Host "Error: Could not locate Scripts directory" -ForegroundColor Red
    Write-Host "Tried:" -ForegroundColor Yellow
    foreach ($path in $possiblePaths) {
        Write-Host "  - $path" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "Please add this path manually to your PATH:" -ForegroundColor Yellow
    Write-Host "1. Press Win+X, select 'System' > 'Advanced system settings'" -ForegroundColor Cyan
    Write-Host "2. Click 'Environment Variables'" -ForegroundColor Cyan
    Write-Host "3. Under 'User variables', select 'Path' > 'Edit'" -ForegroundColor Cyan
    Write-Host "4. Add the Scripts directory path" -ForegroundColor Cyan
    exit 1
}

Write-Host "Found Scripts directory: $foundPath" -ForegroundColor Green

# Check if zeta.exe exists
$zetaExe = Join-Path $foundPath "zeta.exe"
if (-not (Test-Path $zetaExe)) {
    Write-Host "Warning: zeta.exe not found in $foundPath" -ForegroundColor Yellow
    Write-Host "ZETA CLI may not be installed correctly." -ForegroundColor Yellow
    Write-Host "Try: pip install --upgrade zeta-cli" -ForegroundColor Cyan
    exit 1
}

Write-Host "Found zeta.exe: $zetaExe" -ForegroundColor Green

# Get current PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

# Check if already in PATH
if ($currentPath -like "*$foundPath*") {
    Write-Host ""
    Write-Host "✓ Scripts directory is already in PATH!" -ForegroundColor Green
    Write-Host ""
    Write-Host "If 'zeta' command still doesn't work:" -ForegroundColor Yellow
    Write-Host "1. Close this PowerShell window" -ForegroundColor Cyan
    Write-Host "2. Open a NEW PowerShell window" -ForegroundColor Cyan
    Write-Host "3. Try: zeta --version" -ForegroundColor Cyan
    exit 0
}

# Add to PATH
Write-Host ""
Write-Host "Adding to user PATH..." -ForegroundColor Yellow
$newPath = $currentPath + ";$foundPath"
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")

Write-Host ""
Write-Host "✓ Successfully added to PATH!" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Close this PowerShell window completely" -ForegroundColor Cyan
Write-Host "2. Open a NEW PowerShell window" -ForegroundColor Cyan
Write-Host "3. Test with: zeta --version" -ForegroundColor Cyan
Write-Host ""
Write-Host "The 'zeta' command should now work!" -ForegroundColor Green

