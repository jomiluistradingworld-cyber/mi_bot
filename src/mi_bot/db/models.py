from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, Float, JSON, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    personalities: Mapped[List["PersonalityUsage"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    messages: Mapped[List["Message"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    summaries: Mapped[List["MemorySummary"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class PersonalityUsage(Base):
    __tablename__ = "personality_usage"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    personality_key: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="personalities")

class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    personality_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String, nullable=False) # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(String, nullable=False)
    
    # Sentiment Analysis
    sentiment_polarity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sentiment_subjectivity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sentiment_category: Mapped[Optional[str]] = mapped_column(String, nullable=True) # 'positive', 'negative', 'neutral'
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="messages")

class MemorySummary(Base):
    __tablename__ = "memory_summaries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    personality_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
    key_points: Mapped[dict] = mapped_column(JSON, nullable=False) # JSON of key points
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="summaries")
    
    # Constraint: Unique combination of user and personality
    __table_args__ = (
        # Using a simple check for unique constraint via SQLAlchemy
        # (Note: for SQLite we handle this in repository if needed, or via sqlalchemy unique constraint)
    )
