from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from src.mi_bot.db.session import get_db

def get_db_session():
    """FastAPI dependency to get DB session."""
    return get_db()
