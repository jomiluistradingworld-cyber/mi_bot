#!/bin/bash
set -e

echo "🚀 Iniciando instalación de Mi Bot IA Local..."

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data for sentiment analysis
python3 -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

# Create .env from example
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Se ha creado el archivo .env desde .env.example. Por favor, edítalo con tu TELEGRAM_BOT_TOKEN."
fi

# Create model directory
mkdir -p models

echo "✅ Instalación completada. Recuerda configurar tu .env y tener llama-server corriendo."
