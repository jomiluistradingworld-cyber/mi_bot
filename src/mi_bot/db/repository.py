from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update, and_
from src.mi_bot.db.models import User, Message, PersonalityUsage, MemorySummary
from datetime import datetime

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        ).scalar_one_or_none()

    def create_user(self, telegram_id: int, username: Optional[str] = None) -> User:
        user = self.get_user_by_telegram_id(telegram_id)
        if user:
            user.last_seen = datetime.utcnow()
            self.db.commit()
            return user
        
        user = User(telegram_id=telegram_id, username=username)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_message(self, user_id: int, personality_key: str, role: str, content: str, 
                    polarity: float = None, subjectivity: float = None, category: str = None) -> Message:
        msg = Message(
            user_id=user_id,
            personality_key=personality_key,
            role=role,
            content=content,
            sentiment_polarity=polarity,
            sentiment_subjectivity=subjectivity,
            sentiment_category=category
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_recent_messages(self, user_id: int, personality_key: str, limit: int = 15) -> List[Message]:
        return self.db.execute(
            select(Message)
            .where(and_(Message.user_id == user_id, Message.personality_key == personality_key))
            .order_by(Message.created_at.desc())
            .limit(limit)
        ).scalars().all()

class PersonalityRepository:
    def __init__(self, db: Session):
        self.db = db

    def set_active_personality(self, user_id: int, personality_key: str) -> str:
        # Deactivate all others
        self.db.execute(
            update(PersonalityUsage)
            .where(PersonalityUsage.user_id == user_id)
            .values(is_active=False)
        )
        
        # Set active
        usage = self.db.execute(
            select(PersonalityUsage).where(
                and_(PersonalityUsage.user_id == user_id, PersonalityUsage.personality_key == personality_key)
            )
        ).scalar_one_or_none()
        
        if not usage:
            usage = PersonalityUsage(user_id=user_id, personality_key=personality_key, is_active=True)
            self.db.add(usage)
        else:
            usage.is_active = True
            
        self.db.commit()
        return personality_key

    def get_active_personality(self, user_id: int) -> Optional[str]:
        usage = self.db.execute(
            select(PersonalityUsage).where(
                and_(PersonalityUsage.user_id == user_id, PersonalityUsage.is_active == True)
            )
        ).scalar_one_or_none()
        return usage.personality_key if usage else None

class SummaryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self, user_id: int, personality_key: str) -> Optional[dict]:
        summary = self.db.execute(
            select(MemorySummary).where(
                and_(MemorySummary.user_id == user_id, MemorySummary.personality_key == personality_key)
            )
        ).scalar_one_or_none()
        return summary.key_points if summary else None

    def update_summary(self, user_id: int, personality_key: str, key_points: dict):
        summary = self.db.execute(
            select(MemorySummary).where(
                and_(MemorySummary.user_id == user_id, MemorySummary.personality_key == personality_key)
            )
        ).scalar_one_or_none()
        
        if summary:
            summary.key_points = key_points
            summary.updated_at = datetime.utcnow()
        else:
            summary = MemorySummary(user_id=user_id, personality_key=personality_key, key_points=key_points)
            self.db.add(summary)
        
        self.db.commit()
