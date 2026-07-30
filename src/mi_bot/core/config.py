from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import logging

class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Bot token from BotFather")
    
    # LLM
    LLAMA_SERVER_URL: str = "http://localhost:8080/v1"
    LLAMA_MODEL_NAME: str = "local"
    
    # DB
    DATABASE_URL: str = "sqlite:///./mi_bot.db"
    
    # Memory
    MAX_HISTORY_MESSAGES: int = 15
    
    # App
    EXPORT_DIR: str = "./exports"
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

# Basic logging configuration
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mi_bot")
