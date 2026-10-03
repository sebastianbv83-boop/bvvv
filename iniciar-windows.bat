@echo off
chcp 65001 >nul
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo No tienes Python instalado.
  echo Instalalo desde https://www.python.org/downloads/ y marca la casilla "Add Python to PATH".
  pause
  exit /b
)
echo Preparando (solo tarda la primera vez)...
python -m pip install -q -r requirements.txt
python led_control.py
pause
