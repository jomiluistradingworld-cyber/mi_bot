import json
import csv
import os
from typing import List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, User
from src.mi_bot.db.models import Message
from src.mi_bot.core.config import settings

class ExporterService:
    def __init__(self, db: Session):
        self.db = db

    def export_user_messages(self, telegram_id: int, format: str = "json") -> str:
        """
        Exports messages for a specific user.
        Returns the absolute path to the exported file.
        """
        # We need user_id from telegram_id
        user = self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        ).scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")

        messages = self.db.execute(
            select(Message).where(Message.user_id == user.id).order_by(Message.created_at.asc())
        ).scalars().all()
        
        data = []
        for m in messages:
            data.append({
                "timestamp": m.created_at.isoformat(),
                "personality": m.personality_key,
                "role": m.role,
                "content": m.content,
                "sentiment": m.sentiment_category
            })

        filename = f"user_{telegram_id}_{format}.{format}"
        filepath = os.path.join(settings.EXPORT_DIR, filename)
        
        # Ensure dir exists
        os.makedirs(settings.EXPORT_DIR, exist_ok=True)

        if format == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        elif format == "csv":
            with open(filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys() if data else [])
                writer.writeheader()
                writer.writerows(data)
        else:
            raise ValueError("Unsupported format")

        return filepath
