@echo off
:: build-jar.bat - Compiles the project into target\mock-api-1.0.0.jar
:: Run this ONCE. After that, run.bat handles everything.
:: Requirements: Java 17+ (https://adoptium.net)

title LocalMock Builder

echo.
echo  ============================================
echo   LocalMock  -  Build JAR
echo  ============================================
echo.

java -version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Java not found.
    echo  Install from: https://adoptium.net
    pause & exit /b 1
)
echo  OK: Java found

mvn -version >nul 2>&1
if not errorlevel 1 (
    set MVN=mvn
    echo  OK: System Maven found
    goto :build
)

if exist "mvnw.cmd" (
    set MVN=mvnw.cmd
    echo  OK: Maven wrapper found (will download Maven automatically)
    goto :build
)

echo  ERROR: Maven not found.
echo  Install from https://maven.apache.org
echo  Or via Chocolatey:  choco install maven
pause & exit /b 1

:build
echo.
echo  Building... first run downloads dependencies (~50MB, needs internet)
echo.

call %MVN% clean package -DskipTests

if errorlevel 1 (
    echo.
    echo  ERROR: Build failed. See errors above.
    pause & exit /b 1
)

echo.
echo  ============================================
echo   BUILD SUCCESSFUL
echo  ============================================
echo.
echo  JAR: target\mock-api-1.0.0.jar
echo.
echo  Next step: double-click run.bat
echo  ============================================
echo.
pause
