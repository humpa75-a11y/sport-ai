@echo off
echo ==============================================
echo    EERSTE DIVISIE AI - START SCRIPT
echo ==============================================
echo.
echo Starten van server...
start /B python backend/app.py
timeout /t 5 /nobreak >nul
echo.
echo Server draait! Nu testen...
echo.
python test_eerste_divisie.py
