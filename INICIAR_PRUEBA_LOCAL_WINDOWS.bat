@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 -m pip install -r requirements.txt
  py -3 iniciar_prueba_local.py
) else (
  python -m pip install -r requirements.txt
  python iniciar_prueba_local.py
)
pause
