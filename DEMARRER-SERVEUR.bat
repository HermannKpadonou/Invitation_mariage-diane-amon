@echo off
title Serveur Mariage Diane et Amon
cd /d "%~dp0backend"
if not exist "app\main.py" (
  echo [ERREUR] Dossier backend introuvable.
  pause
  exit /b 1
)
echo ===========================================
echo   Invitation et serveur - Diane et Amon
echo ===========================================
echo.
python -c "import fastapi" 2>nul
if errorlevel 1 (
  echo [1/2] Premiere installation des dependances, patientez...
  pip install -r requirements.txt
  echo.
)
echo [2/2] Demarrage du serveur : http://127.0.0.1:8010
echo   Invitation : http://127.0.0.1:8010
echo   Admin      : http://127.0.0.1:8010/admin.html
echo   Documentation API : http://127.0.0.1:8010/docs
echo Pour arreter : appuyez sur Ctrl + C
echo.
start "" /b cmd /c "timeout /t 3 >nul && start http://127.0.0.1:8010"
python -m uvicorn app.main:app --port 8010
pause
