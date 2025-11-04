# Demo workflow script for ZETA CLI (PowerShell)
# This demonstrates a typical ZETA usage session

Write-Host "=== ZETA CLI Demo Workflow ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Creating a simple Python script..." -ForegroundColor Yellow
zeta run "create a Python script that prints 'Hello, ZETA!'"

Write-Host ""
Write-Host "2. Creating a webpage with teaching mode..." -ForegroundColor Yellow
zeta run "create an HTML page with a heading and a button" --teach

Write-Host ""
Write-Host "3. Reviewing code with critic mode..." -ForegroundColor Yellow
zeta run "review my Python files" --critic

Write-Host ""
Write-Host "4. Viewing learning log..." -ForegroundColor Yellow
zeta log

Write-Host ""
Write-Host "=== Demo Complete ===" -ForegroundColor Green

