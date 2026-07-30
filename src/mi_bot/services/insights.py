from typing import Dict, Any
from sqlalchemy.orm import Session
from src.mi_bot.db.repository import MessageRepository, UserRepository
from src.mi_bot.core.llm_client import llm_client
from src.mi_bot.core.config import settings

class InsightService:
    def __init__(self, db: Session):
        self.db = db
        self.msg_repo = MessageRepository(db)
        self.user_repo = UserRepository(db)

    def generate_user_insights(self, telegram_id: int) -> Dict[str, Any]:
        """
        Uses AI to analyze user patterns and generate insights.
        """
        user = self.user_repo.get_user_by_telegram_id(telegram_id)
        if not user:
            return {"error": "User not found"}
        
        # Fetch last 50 messages to get a pattern
        messages = self.db.execute(
            select(Message).where(Message.user_id == user.id).order_by(Message.created_at.desc()).limit(50)
        ).scalars().all()
        
        if not messages:
            return {"insights": "No hay suficientes mensajes para generar insights."}

        # Prepare a text representation of messages
        conv_text = "\n".join([f"{m.role}: {m.content}" for m in reversed(messages)])
        
        prompt = (
            "Eres un analista de datos emocionales y comportamiento humano. "
            "Analiza el siguiente historial de mensajes y genera un reporte de insights. "
            "Incluye: patrones emocionales, temas recurrentes y una recomendación personalizada para el usuario. "
            "Devuelve el resultado estrictamente en formato JSON con las llaves: 'patrones_emocionales', 'temas_recurrentes', 'recomendacion'."
        )
        
        messages_llm = [{"role": "system", "content": prompt}, {"role": "user", "content": conv_text}]
        response_text = llm_client.generate_response(messages_llm)
        
        try:
            import json
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                return json.loads(response_text[start_idx:end_idx])
        except Exception as e:
            from src.mi_bot.core.config import logger
            logger.error(f"Error parsing insights JSON: {e}")
        
        return {"error": "No se pudieron generar insights automatizados."}
