@echo off
REM 📤 Upload De Meester naar DigitalOcean Server
REM Gebruik: upload_to_server.bat YOUR_SERVER_IP

echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║                                                                      ║
echo ║           📤 DE MEESTER - UPLOAD NAAR SERVER 📤                      ║
echo ║                                                                      ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

if "%1"=="" (
    echo ❌ ERROR: Geen server IP opgegeven!
    echo.
    echo Gebruik: upload_to_server.bat YOUR_SERVER_IP
    echo Voorbeeld: upload_to_server.bat 164.90.123.45
    echo.
    pause
    exit /b 1
)

set SERVER_IP=%1
set SERVER_USER=demeester
set SERVER_PATH=/home/demeester/sport-ai

echo 🎯 Server: %SERVER_USER%@%SERVER_IP%
echo 📁 Doel: %SERVER_PATH%
echo.
echo 📦 Uploading bestanden...
echo.

REM Upload backend
echo [1/5] Uploading backend...
scp -r backend %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/

REM Upload frontend
echo [2/5] Uploading frontend...
scp -r frontend %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/

REM Upload scripts
echo [3/5] Uploading scripts...
scp -r scripts %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/

REM Upload data
echo [4/5] Uploading data...
scp -r data %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/

REM Upload requirements
echo [5/5] Uploading requirements.txt...
scp requirements.txt %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/

echo.
echo ✅ Upload compleet!
echo.
echo 🔄 Herstart nu de server met:
echo    ssh %SERVER_USER%@%SERVER_IP%
echo    sudo supervisorctl restart demeester
echo.
pause
