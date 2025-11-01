@echo off
echo ================================================================================
echo    🚀 DE MEESTER - PERMANENT SERVER STARTUP 🚀
echo ================================================================================
echo.
echo Starting server on http://localhost:5000
echo This server will keep running in the background...
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

cd /d "%~dp0"
".venv\Scripts\python.exe" backend\app.py

pause
