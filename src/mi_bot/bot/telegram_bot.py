import telebot
from telebot import types
from sqlalchemy.orm import Session

from src.mi_bot.core.config import settings, logger
from src.mi_bot.core.personalities import PERSONALITY_COMMANDS, get_personality_prompt
from src.mi_bot.core.llm_client import llm_client
from src.mi_bot.db.session import SessionLocal
from src.mi_bot.db.repository import UserRepository, MessageRepository, PersonalityRepository, SummaryRepository
from src.mi_bot.services.memory import MemoryService
from src.mi_bot.services.sentiment import SentimentService
from src.mi_bot.bot.keyboards import main_menu, help_keyboard

class TelegramBot:
    def __init__(self):
        self.bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)
        self.setup_handlers()

    def setup_handlers(self):
        # Base commands
        self.bot.add_message_handler(self.handle_start, commands=['start'])
        self.bot.add_message_handler(self.handle_help, commands=['help'])
        self.bot.add_callback_query_handler(self.handle_personality_callback, func=lambda call: call.data.startswith('set_personality_'))
        
        # Personality commands
        for cmd, key in PERSONALITY_COMMANDS.items():
            self.bot.add_message_handler(
                lambda message, k=key: self.handle_personality_command(message, k), 
                commands=[cmd[1:]]
            )
            
        # Other utils
        self.bot.add_message_handler(self.handle_export, commands=['exportar'])
        self.bot.add_message_handler(self.handle_insights, commands=['insights'])
        self.bot.add_message_handler(self.handle_reset, commands=['reset'])
        
        # Default text handler
        self.bot.add_message_handler(self.handle_text)

    def handle_start(self, message):
        db = SessionLocal()
        try:
            user_repo = UserRepository(db)
            user = user_repo.create_user(message.chat.id, message.from_user.username)
            
            self.bot.send_message(
                message.chat.id, 
                "¡Hola! Soy tu asistente de IA local. Puedo adoptar diferentes personalidades según lo que necesites.\n\nSelecciona una personalidad abajo para comenzar:",
                reply_markup=main_menu()
            )
        finally:
            db.close()

    def handle_help(self, message):
        help_text = (
            "📚 *Comandos Disponibles:*\n\n"
            "/start - Reiniciar el bot y menú de personalidades\n"
            "/help - Ver esta ayuda\n"
            "/reset - Borrar historial de la personalidad actual\n"
            "/exportar - Exportar conversaciones a JSON/CSV\n"
            "/insights - Generar análisis de patrones con IA\n\n"
            "🎭 *Personalidades:*\n"
            "Usa los botones del menú o comandos como /amigo, /sabio, /motivador, etc."
        )
        self.bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

    def handle_personality_command(self, message, key):
        db = SessionLocal()
        try:
            user_repo = UserRepository(db)
            user = user_repo.get_user_by_telegram_id(message.chat.id)
            p_repo = PersonalityRepository(db)
            p_repo.set_active_personality(user.id, key)
            
            names = {"amigo": "Amigo", "motivador": "Motivador", "sabio": "Sabio", "humorista": "Humorista", "mentor": "Mentor", "apoyo": "Apoyo"}
            self.bot.send_message(message.chat.id, f"✅ Personalidad cambiada a: *{names.get(key, key)}*", parse_mode="Markdown")
        finally:
            db.close()

    def handle_personality_callback(self, call):
        key = call.data.replace('set_personality_', '')
        db = SessionLocal()
        try:
            user_repo = UserRepository(db)
            user = user_repo.get_user_by_telegram_id(call.message.chat.id)
            p_repo = PersonalityRepository(db)
            p_repo.set_active_personality(user.id, key)
            
            names = {"amigo": "Amigo", "motivador": "Motivador", "sabio": "Sabio", "humorista": "Humorista", "mentor": "Mentor", "apoyo": "Apoyo"}
            self.bot.answer_callback_query(call.id, f"Personalidad: {names.get(key, key)}")
            self.bot.send_message(call.message.chat.id, f"✅ Ahora estoy en modo *{names.get(key, key)}*. ¡Cuéntame lo que quieras!", parse_mode="Markdown")
        finally:
            db.close()

    def handle_text(self, message):
        db = SessionLocal()
        try:
            user_repo = UserRepository(db)
            user = user_repo.create_user(message.chat.id, message.from_user.username)
            
            p_repo = PersonalityRepository(db)
            active_key = p_repo.get_active_personality(user.id)
            
            if not active_key:
                self.bot.send_message(message.chat.id, "Por favor, selecciona una personalidad primero usando /start")
                return

            # 1. Save user message
            sentiment = SentimentService.analyze(message.text)
            msg_repo = MessageRepository(db)
            msg_repo.add_message(
                user_id=user.id,
                personality_key=active_key,
                role="user",
                content=message.text,
                polarity=sentiment["polarity"],
                subjectivity=sentiment["subjectivity"],
                category=sentiment["category"]
            )
            
            # 2. Build Context
            mem_service = MemoryService(db)
            system_prompt = get_personality_prompt(active_key)
            summary = mem_service.get_summarized_memory(user.id, active_key)
            history = mem_service.get_context_messages(user.id, active_key)
            
            full_system = f"{system_prompt}\n\nMemoria Reciente:\n{summary if summary else 'Sin memoria previa.'}"
            messages = [{"role": "system", "content": full_system}] + history + [{"role": "user", "content": message.text}]
            
            # 3. LLM Call
            response_text = llm_client.generate_response(messages)
            
            # 4. Save assistant response
            msg_repo.add_message(
                user_id=user.id,
                personality_key=active_key,
                role="assistant",
                content=response_text
            )
            
            self.bot.send_message(message.chat.id, response_text)
            
            # Background task: update memory summary occasionally
            # For simplicity here, we just do it every 5 messages
            all_msgs = msg_repo.get_recent_messages(user.id, active_key, limit=10)
            if len(all_msgs) % 5 == 0:
                mem_service.generate_summary_with_ai(user.id, active_key)

        except Exception as e:
            logger.error(f"Error in handle_text: {e}")
            self.bot.send_message(message.chat.id, "Hubo un error procesando tu mensaje. Intenta de nuevo.")
        finally:
            db.close()

    def handle_export(self, message):
        db = SessionLocal()
        try:
            from src.mi_bot.services.exporter import ExporterService
            exp_service = ExporterService(db)
            path = exp_service.export_user_messages(message.chat.id, format="json")
            
            with open(path, "rb") as f:
                self.bot.send_document(message.chat.id, f, caption="Aquí tienes tu exportación en formato JSON.")
        except Exception as e:
            logger.error(f"Error exporting messages: {e}")
            self.bot.send_message(message.chat.id, "Error al exportar mensajes. Asegúrate de haber hablado con el bot.")
        finally:
            db.close()

    def handle_insights(self, message):
        db = SessionLocal()
        try:
            from src.mi_bot.services.insights import InsightService
            ins_service = InsightService(db)
            result = ins_service.generate_user_insights(message.chat.id)
            
            if "error" in result:
                self.bot.send_message(message.chat.id, result["error"])
            else:
                text = (
                    f"🧠 *Insights de tu Conversación:*\n\n"
                    f"📉 *Patrones Emocionales:* {result.get('patrones_emocionales', 'N/A')}\n"
                    f"🔑 *Temas Recurrentes:* {result.get('temas_recurrentes', 'N/A')}\n"
                    f"💡 *Sugerencia:* {result.get('recomendacion', 'N/A')}"
                )
                self.bot.send_message(message.chat.id, text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            self.bot.send_message(message.chat.id, "Error al generar insights.")
        finally:
            db.close()

    def handle_reset(self, message):
        db = SessionLocal()
        try:
            # For simplicity: just clear messages for active personality
            user_repo = UserRepository(db)
            user = user_repo.get_user_by_telegram_id(message.chat.id)
            p_repo = PersonalityRepository(db)
            active_key = p_repo.get_active_personality(user.id)
            
            if active_key:
                # Bulk delete
                from src.mi_bot.db.models import Message
                from sqlalchemy import delete, and_
                self.db = db # Local ref for the a la carte delete
                self.db.execute(delete(Message).where(
                    and_(Message.user_id == user.id, Message.personality_key == active_key)
                ))
                self.db.commit()
                self.bot.send_message(message.chat.id, "Historial de la personalidad actual borrado.")
            else:
                self.bot.send_message(message.chat.id, "No tienes una personalidad activa.")
        except Exception as e:
            logger.error(f"Error resetting history: {e}")
            self.bot.send_message(message.chat.id, "Error al resetear historial.")
        finally:
            db.close()

    def run(self):
        logger.info("Starting Telegram Bot...")
        self.bot.polling(non_stop=True)
