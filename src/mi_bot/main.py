import threading
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.mi_bot.api.routes import router as api_router
from src.mi_bot.bot.telegram_bot import TelegramBot
from src.mi_bot.db.session import init_db
from src.mi_bot.core.config import logger

app = FastAPI(title="Mi Bot IA Local Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory="src/mi_bot/web/static"), name="static")

# Include API routes
app.include_router(api_router)

def run_bot():
    """Thread function to start the Telegram bot."""
    try:
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        logger.error(f"Bot failure: {e}")

@app.on_event("startup")
async def startup_event():
    # 1. Init Database
    init_db()
    logger.info("Database initialized.")
    
    # 2. Start Bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("Telegram Bot started in background thread.")

if __name__ == "__main__":
    # Start FastAPI with uvicorn
    uvicorn.run(
        "src.mi_bot.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False
    )
