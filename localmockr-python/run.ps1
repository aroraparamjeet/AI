# LocalMockr - PowerShell Run Script
# Usage: Right-click -> Run with PowerShell
#        OR in PowerShell: .\run.ps1

Set-Location $PSScriptRoot

Write-Host ""
Write-Host "  ==========================================" -ForegroundColor Cyan
Write-Host "   LocalMockr v2  -  API Proxy & Mock Studio" -ForegroundColor Cyan
Write-Host "  ==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pyver = python --version 2>&1
    Write-Host "  Found: $pyver" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Python not found. Download from https://python.org" -ForegroundColor Red
    Read-Host "  Press Enter to exit"
    exit 1
}

# Check ui.html exists
if (-not (Test-Path "ui.html")) {
    Write-Host "  [ERROR] ui.html not found in this folder." -ForegroundColor Red
    Write-Host "  Make sure ui.html and localmockr.py are in the same folder." -ForegroundColor Red
    Read-Host "  Press Enter to exit"
    exit 1
}

Write-Host "  Starting LocalMockr..." -ForegroundColor Yellow
Write-Host "  Dashboard -> http://localhost:3848" -ForegroundColor White
Write-Host "  Proxy     -> http://localhost:3847" -ForegroundColor White
Write-Host "  Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

python localmockr.py
