# Setup script for pre-commit hooks (PowerShell)

Write-Host "Setting up pre-commit hooks..." -ForegroundColor Cyan

# Install pre-commit if not already installed
try {
    pre-commit --version | Out-Null
    Write-Host "Pre-commit is already installed." -ForegroundColor Green
} catch {
    Write-Host "Installing pre-commit..." -ForegroundColor Yellow
    pip install pre-commit
}

# Install hooks
pre-commit install

Write-Host ""
Write-Host "Pre-commit hooks installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Hooks will run automatically on git commit." -ForegroundColor Cyan
Write-Host "To run manually: pre-commit run --all-files" -ForegroundColor Cyan

