from typing import List, Dict
from sqlalchemy.orm import Session
from src.mi_bot.db.repository import MessageRepository, SummaryRepository
from src.mi_bot.core.llm_client import llm_client
from src.mi_bot.core.config import settings

class MemoryService:
    def __init__(self, db: Session):
        self.msg_repo = MessageRepository(db)
        self.sum_repo = SummaryRepository(db)

    def get_context_messages(self, user_id: int, personality_key: str) -> List[Dict[str, str]]:
        """Returns recent messages as OpenAI-style chat history."""
        messages = self.msg_repo.get_recent_messages(user_id, personality_key, limit=settings.MAX_HISTORY_MESSAGES)
        # Messages are DESC, reverse them for chronological order
        history = []
        for msg in reversed(messages):
            history.append({"role": msg.role, "content": msg.content})
        return history

    def get_summarized_memory(self, user_id: int, personality_key: str) -> str:
        """Returns a string representation of summarized key points."""
        summary = self.sum_repo.get_summary(user_id, personality_key)
        if not summary:
            return ""
        
        points = []
        for key, value in summary.items():
            points.append(f"{key}: {value}")
        
        return "\n".join(points)

    def update_memory_summary(self, user_id: int, personality_key: str, new_points: Dict[str, str]):
        """Saves a new summary to the DB."""
        self.sum_repo.update_summary(user_id, personality_key, new_points)

    def generate_summary_with_ai(self, user_id: int, personality_key: str):
        """Analyzes recent history and updates the memory summary using the LLM."""
        history = self.get_context_messages(user_id, personality_key)
        if not history:
            return
        
        prompt = (
            "Analiza el siguiente historial de conversación y extrae los puntos clave, "
            "preferencias del usuario, hechos importantes y temas recurrentes. "
            "Devuelve la respuesta estrictamente como un diccionario JSON donde las llaves sean el tema "
            "y el valor sea la descripción breve. Ejemplo: {'Intereses': 'Le gusta el senderismo', 'Meta': 'Aprender Python'}"
        )
        
        messages = [{"role": "system", "content": prompt}] + history
        response_text = llm_client.generate_response(messages)
        
        try:
            # Simple cleanup of response text to find JSON
            import json
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                points = json.loads(json_str)
                self.update_memory_summary(user_id, personality_key, points)
        except Exception as e:
            from src.mi_bot.core.config import logger
            logger.error(f"Error updating memory summary with AI: {e}")
