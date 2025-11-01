@echo off
echo ================================================================================
echo    🧠 DE MEESTER - AI TRAINING (Server blijft draaien) 🧠
echo ================================================================================
echo.
echo BELANGRIJK: Deze training stopt de server NIET!
echo De server blijft gewoon draaien op http://localhost:5000
echo.
echo Training wordt nu gestart...
echo ================================================================================
echo.

cd /d "%~dp0"
".venv\Scripts\python.exe" scripts\train_model.py

echo.
echo ================================================================================
echo    ✅ TRAINING VOLTOOID!
echo    🌐 Server draait nog steeds op http://localhost:5000
echo ================================================================================
echo.
pause
