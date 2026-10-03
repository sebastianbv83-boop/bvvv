#!/bin/bash
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null; then
  echo "No tienes Python instalado. Descárgalo de https://www.python.org/downloads/"
  read -p "Pulsa Enter para cerrar"
  exit 1
fi
echo "Preparando (solo tarda la primera vez)..."
python3 -m pip install -q --user -r requirements.txt
python3 led_control.py
read -p "Pulsa Enter para cerrar"
