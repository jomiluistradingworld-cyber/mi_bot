"""
Simple Telegram bot skeleton (python-telegram-bot v22+).
"""

from telegram.ext import CommandHandler, MessageHandler, ApplicationBuilder, filters
import logging
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


async def echo(update, context):
    """Echo back any text message."""
    chat_id = update.effective_chat.id
    text = update.message.text
    await context.bot.send_message(chat_id=chat_id, text=text)


async def start(update, context):
    """Handle /start command."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hola! I am a bot. Send a message and I will echo it.")


def start_bot():
    """Start the bot with basic echo command."""
    application = ApplicationBuilder().token(BOT_TOKEN or "").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling(timeout=120)


if __name__ == "__main__":
    start_bot()
