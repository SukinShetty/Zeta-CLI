# ZETA CLI Setup Checker for Windows
# Run this script to verify your installation

Write-Host "`n=== ZETA CLI Setup Checker ===" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Python not found!" -ForegroundColor Red
    Write-Host "   Install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    $allGood = $false
}

# Check ZETA CLI installation
Write-Host "`n2. Checking ZETA CLI..." -ForegroundColor Yellow
try {
    $zetaVersion = python -m zeta --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ ZETA CLI: $zetaVersion" -ForegroundColor Green
    } else {
        throw "Not installed"
    }
} catch {
    Write-Host "   ✗ ZETA CLI not found!" -ForegroundColor Red
    Write-Host "   Install with: pip install zeta-cli" -ForegroundColor Yellow
    $allGood = $false
}

# Check if 'zeta' command works
Write-Host "`n3. Checking 'zeta' command..." -ForegroundColor Yellow
try {
    $zetaCmd = zeta --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ 'zeta' command works: $zetaCmd" -ForegroundColor Green
    } else {
        throw "Not in PATH"
    }
} catch {
    Write-Host "   ⚠ 'zeta' command not in PATH" -ForegroundColor Yellow
    Write-Host "   Use 'python -m zeta' instead (recommended for Windows)" -ForegroundColor Cyan
}

# Check Ollama
Write-Host "`n4. Checking Ollama..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Ollama: $ollamaVersion" -ForegroundColor Green
    } else {
        throw "Not found"
    }
} catch {
    Write-Host "   ✗ Ollama not found!" -ForegroundColor Red
    Write-Host "   Download from: https://ollama.ai/download" -ForegroundColor Yellow
    Write-Host "   After installation, restart PowerShell!" -ForegroundColor Yellow
    $allGood = $false
}

# Check model
Write-Host "`n5. Checking minimax-m2:cloud model..." -ForegroundColor Yellow
try {
    $modelList = ollama list 2>&1
    if ($modelList -match "minimax-m2") {
        Write-Host "   ✓ Model installed" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Model not installed" -ForegroundColor Yellow
        Write-Host "   Run: ollama pull minimax-m2:cloud" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ⚠ Could not check model (Ollama may not be running)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "✓ All core components are installed!" -ForegroundColor Green
    Write-Host "`nTry: python -m zeta run 'create a simple text file'" -ForegroundColor Cyan
} else {
    Write-Host "⚠ Some components are missing. See fixes above." -ForegroundColor Yellow
}

Write-Host "`nFor Windows, use: python -m zeta <command>" -ForegroundColor Cyan
Write-Host "This avoids PATH issues entirely!`n" -ForegroundColor Yellow

