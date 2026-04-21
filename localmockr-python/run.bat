@echo off
:: ============================================================
::  LocalMockr - Run Script (no build needed)
::  Just runs localmockr.py directly with Python.
::  Requirements: Python 3.8+ installed and on PATH
:: ============================================================

title LocalMockr
chcp 65001 >nul

echo.
echo  ==========================================
echo   LocalMockr v2  -  API Proxy ^& Mock Studio
echo  ==========================================
echo.

:: Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found on PATH.
    echo  Download from https://python.org
    echo  Make sure "Add Python to PATH" is checked during install.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo  Found: %%v
echo.

:: Change to the folder containing this bat file so relative paths work
cd /d "%~dp0"

:: Check ui.html is present
if not exist "ui.html" (
    echo  [ERROR] ui.html not found in this folder.
    echo  Make sure ui.html and localmockr.py are in the same folder as this run.bat
    pause
    exit /b 1
)

echo  Starting LocalMockr...
echo  Dashboard will open automatically at http://localhost:3848
echo  Proxy listening at http://localhost:3847
echo.
echo  Press Ctrl+C to stop.
echo.

python localmockr.py

pause
