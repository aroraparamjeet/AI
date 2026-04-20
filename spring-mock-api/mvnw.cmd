@echo off
:: Maven Wrapper for Windows
:: Downloads Maven automatically on first run - no manual Maven install needed.

setlocal

set MAVEN_VERSION=3.9.6
set MAVEN_DIR=%USERPROFILE%\.m2\wrapper\apache-maven-%MAVEN_VERSION%
set MVN_CMD=%MAVEN_DIR%\bin\mvn.cmd
set DOWNLOAD_URL=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/%MAVEN_VERSION%/apache-maven-%MAVEN_VERSION%-bin.zip
set ZIP_FILE=%TEMP%\apache-maven-%MAVEN_VERSION%-bin.zip

if exist "%MVN_CMD%" goto :run

echo Maven %MAVEN_VERSION% not found. Downloading (one-time, ~10MB)...
echo.

powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%ZIP_FILE%'"

if errorlevel 1 (
    echo.
    echo  ERROR: Maven download failed. Check internet connection.
    echo  Or install Maven manually: https://maven.apache.org/download.cgi
    exit /b 1
)

echo Extracting Maven...
powershell -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%USERPROFILE%\.m2\wrapper\' -Force"
del "%ZIP_FILE%"

if not exist "%MVN_CMD%" (
    echo  ERROR: Maven extraction failed.
    exit /b 1
)

echo Maven %MAVEN_VERSION% ready.
echo.

:run
call "%MVN_CMD%" %*
