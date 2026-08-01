import os
from dotenv import load_dotenv

# Load .env for Telegram token if present
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USUARIO_ID = os.getenv("USUARIO_ID")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN not set in environment or .env")

# Expose bot token and user ID for other modules
__all__ = ["BOT_TOKEN", "USUARIO_ID"]
