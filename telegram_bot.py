"""
Simple Telegram bot skeleton.
"""

from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
import logging
from .config import BOT_TOKEN

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def echo(update, context):
    """Echo back any text message."""
    chat_id = update.effective_chat.id
    text = update.message.text
    context.bot.send_message(chat_id=chat_id, text=text)


def start_bot():
    """Start the bot with basic echo command."""
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", lambda u, c: c.bot.send_message(chat_id=u.effective_chat.id, text="Hola! I am a bot. Send a message and I will echo it.")))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling(timeout=120, read_latency=2)
    updater.idle()


if __name__ == "__main__":
    start_bot()
