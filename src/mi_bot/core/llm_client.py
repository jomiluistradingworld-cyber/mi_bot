from openai import OpenAI
from src.mi_bot.core.config import settings, logger
from typing import List, Dict

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.LLAMA_SERVER_URL,
            api_key="no-key-required" # llama.cpp doesn't need one
        )
        self.model = settings.LLAMA_MODEL_NAME

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generates a response using the local llama-server.
        
        Args:
            messages: List of chat messages (role and content).
        Returns:
            The generated text response.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=512
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response from LLM: {e}")
            return "Lo siento, estoy teniendo problemas técnicos para procesar tu mensaje. ¿Podemos intentar de nuevo?"

# Singleton instance
llm_client = LLMClient()
