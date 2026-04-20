@echo off
:: LocalMock Spring Boot API - run.bat
:: Double-click to build (if needed) and start the mock server
:: Mock server runs on: http://localhost:8081
:: Requirements: Java 17+ (https://adoptium.net)

title LocalMock Spring Boot API

echo.
echo  ============================================
echo   LocalMock  -  Spring Boot API Server
echo  ============================================
echo.

:: Check Java
java -version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Java not found!
    echo  Install Java 17 from: https://adoptium.net
    echo  Check "Add to PATH" during install, then restart.
    pause
    exit /b 1
)
echo  OK: Java detected
echo.

:: Build JAR if not already built
if exist "target\mock-api-1.0.0.jar" (
    echo  OK: JAR already built - skipping build
    goto :start_server
)

echo  Building project...
echo  First run downloads Maven and Spring Boot (~50MB, needs internet)
echo  This takes 2-3 minutes. Subsequent runs are instant.
echo.

mvn -version >nul 2>&1
if not errorlevel 1 (
    echo  Using system Maven...
    call mvn clean package -DskipTests
    goto :check_build
)

if exist "mvnw.cmd" (
    echo  Using Maven wrapper (auto-downloads Maven)...
    call mvnw.cmd clean package -DskipTests
    goto :check_build
)

echo  ERROR: Maven not found. Install from https://maven.apache.org
pause
exit /b 1

:check_build
if not exist "target\mock-api-1.0.0.jar" (
    echo.
    echo  ERROR: Build failed. Check errors above.
    pause
    exit /b 1
)
echo.
echo  OK: Build successful

:start_server
echo.
echo  ============================================
echo   Mock API running at http://localhost:8081
echo  ============================================
echo.
echo  Endpoints:
echo    GET  http://localhost:8081/api/customer/health
echo    GET  http://localhost:8081/api/customer/bankdetails
echo    GET  http://localhost:8081/api/customer/bankdetails/{id}
echo    POST http://localhost:8081/api/customer/bankdetails
echo    DEL  http://localhost:8081/api/customer/bankdetails/{id}
echo.
echo  Test IDs: NOTFOUND (404)  FORBIDDEN (403)
echo  Set your app base URL to: http://localhost:8081
echo  All responses contain "source": "LOCAL_MOCK"
echo.
echo  Press Ctrl+C to stop.
echo  ============================================
echo.

java -jar target\mock-api-1.0.0.jar

echo.
echo  Server stopped.
pause
