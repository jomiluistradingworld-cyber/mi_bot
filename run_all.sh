#!/bin/bash
set -e

echo "🤖 Iniciando Mi Bot IA Local..."

# Activate venv
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
else
    echo "❌ No se encontró el entorno virtual. Ejecuta ./setup.sh primero."
    exit 1
fi

# Start the main application
python3 src/mi_bot/main.py
