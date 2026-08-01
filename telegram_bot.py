"""
Telegram bot using local Ollama model (goekdenizguelmez/JOSIE:4b-instruct).
"""
import logging
import ollama
from telegram import constants
from telegram.ext import CommandHandler, MessageHandler, ApplicationBuilder, filters
from config import BOT_TOKEN, USUARIO_ID

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OLLAMA_MODEL = "goekdenizguelmez/JOSIE:4b-instruct"
SYSTEM_PROMPT = "Eres un asistente de inteligencia artificial útil, empático y amable. Respondes siempre en español."


async def start(update, context):
    """Handle /start command."""
    user_id = str(update.effective_user.id)
    if USUARIO_ID and user_id != str(USUARIO_ID):
        logger.warning(f"Unauthorized access attempt from user_id: {user_id}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Acceso no autorizado.",
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="¡Hola! Soy tu bot con IA local impulsado por Ollama. Envíame cualquier mensaje y te responderé.",
    )


async def handle_message(update, context):
    """Handle incoming text messages and generate a response using Ollama."""
    user_id = str(update.effective_user.id)
    if USUARIO_ID and user_id != str(USUARIO_ID):
        logger.warning(f"Unauthorized message from user_id: {user_id}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Acceso no autorizado.",
        )
        return

    chat_id = update.effective_chat.id
    user_message = update.message.text

    # Indicate typing state to Telegram user
    await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)

    try:
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=f"{SYSTEM_PROMPT}\nUsuario: {user_message}\nAsistente:",
            stream=False,
        )
        bot_response = response.get("response", "Lo siento, no pude generar una respuesta.")
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        bot_response = "Lo siento, ocurrió un error al consultar el modelo de IA local."

    await context.bot.send_message(chat_id=chat_id, text=bot_response)


def start_bot():
    """Start the bot."""
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing!")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info(f"Bot iniciado correctamente. Usando el modelo Ollama '{OLLAMA_MODEL}'...")
    application.run_polling(timeout=120)


if __name__ == "__main__":
    start_bot()
