# Release script for ZETA CLI (PowerShell)
# Usage: .\scripts\release.ps1 <version>

param(
    [Parameter(Mandatory=$true)]
    [string]$Version
)

Write-Host "Releasing ZETA CLI version $Version" -ForegroundColor Cyan
Write-Host ""

# Check if we're on main branch
$currentBranch = git branch --show-current
if ($currentBranch -ne "main" -and $currentBranch -ne "master") {
    Write-Host "Warning: You're not on main/master branch. Current branch: $currentBranch" -ForegroundColor Yellow
    $response = Read-Host "Continue anyway? (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
}

# Update version in setup.py
Write-Host "Updating version in setup.py..." -ForegroundColor Yellow
$setupContent = Get-Content setup.py -Raw
$setupContent = $setupContent -replace 'version="[^"]*"', "version=`"$Version`""
Set-Content setup.py -Value $setupContent -NoNewline

# Update version in zeta.py if __version__ exists
if (Select-String -Path zeta.py -Pattern "__version__") {
    Write-Host "Updating version in zeta.py..." -ForegroundColor Yellow
    $zetaContent = Get-Content zeta.py -Raw
    $zetaContent = $zetaContent -replace '__version__ = "[^"]*"', "__version__ = `"$Version`""
    Set-Content zeta.py -Value $zetaContent -NoNewline
}

# Run tests
Write-Host "Running tests..." -ForegroundColor Yellow
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed! Aborting release." -ForegroundColor Red
    exit 1
}

# Build package
Write-Host "Building package..." -ForegroundColor Yellow
python -m build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed! Aborting release." -ForegroundColor Red
    exit 1
}

# Check package
Write-Host "Checking package..." -ForegroundColor Yellow
twine check dist/*
if ($LASTEXITCODE -ne 0) {
    Write-Host "Package check failed! Aborting release." -ForegroundColor Red
    exit 1
}

# Create git tag
Write-Host "Creating git tag v$Version..." -ForegroundColor Yellow
git add setup.py zeta.py
git commit -m "Bump version to $Version" 2>$null
git tag -a "v$Version" -m "Release version $Version"

Write-Host ""
Write-Host "Release preparation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Review changes: git diff HEAD~1"
Write-Host "2. Push tag: git push origin v$Version"
Write-Host "3. Push commits: git push"
Write-Host "4. Upload to PyPI: twine upload dist/*"
Write-Host ""
Write-Host "Or use GitHub Actions release workflow for automated release." -ForegroundColor Yellow

