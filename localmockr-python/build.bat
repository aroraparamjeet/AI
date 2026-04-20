@echo off
:: ============================================================
::  LocalMockr - Windows Build Script
::  Produces:  dist\LocalMockr.exe
:: ============================================================

title LocalMockr Builder
chcp 65001 >nul

echo.
echo  ============================================
echo   LocalMockr - Build Script
echo  ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found.
    echo  Download from https://python.org
    echo  Make sure "Add Python to PATH" is checked during install.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo  Found: %%v

:: Create virtual environment
if not exist ".venv" (
    echo.
    echo  Creating virtual environment...
    python -m venv .venv
)

echo  Activating virtual environment...
call .venv\Scripts\activate.bat

:: Install PyInstaller
echo.
echo  Installing PyInstaller (one-time, needs internet)...
pip install --quiet --upgrade pip
pip install --quiet pyinstaller

:: Embed HTML into Python source
echo.
echo  Embedding UI...
python embed_ui.py
if errorlevel 1 (
    echo  [ERROR] embed_ui.py failed.
    pause
    exit /b 1
)

:: Build with PyInstaller
echo.
echo  Building executable (30-60 seconds)...
echo.

pyinstaller ^
    --onefile ^
    --console ^
    --name LocalMockr ^
    --clean ^
    --noconfirm ^
    localmockr_embedded.py

if errorlevel 1 (
    echo.
    echo  [ERROR] Build failed. See above for details.
    pause
    exit /b 1
)

echo.
echo  ============================================
echo   BUILD SUCCESSFUL
echo  ============================================
echo.
echo   Run it:  double-click dist\LocalMockr.exe
echo            OR from PowerShell: .\dist\LocalMockr.exe
echo.
echo   The exe is self-contained - copy it anywhere.
echo  ============================================
echo.

set /p LAUNCH="  Launch now? (y/n): "
if /i "%LAUNCH%"=="y" start "" dist\LocalMockr.exe

pause
