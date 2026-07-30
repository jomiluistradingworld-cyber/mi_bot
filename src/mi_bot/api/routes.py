from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from src.mi_bot.api.deps import get_db_session
from src.mi_bot.db.repository import UserRepository, MessageRepository, PersonalityRepository
from src.mi_bot.db.models import User, Message
from src.mi_bot.core.config import settings
from src.mi_bot.services.exporter import ExporterService
from src.mi_bot.services.insights import InsightService
from sqlalchemy import select, func

router = APIRouter()
templates = Jinja2Templates(directory="src/mi_bot/web/templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db_session)):
    # Global stats
    user_count = db.execute(select(func.count(User.id))).scalar()
    msg_count = db.execute(select(func.count(Message.id))).scalar()
    
    # Get last 10 users for the table
    users = db.execute(
        select(User).order_by(User.last_seen.desc()).limit(10)
    ).scalars().all()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user_count": user_count,
        "msg_count": msg_count,
        "users": users
    })

@router.get("/api/stats")
async def get_stats(db: Session = Depends(get_db_session)):
    user_count = db.execute(select(func.count(User.id))).scalar()
    msg_count = db.execute(select(func.count(Message.id))).scalar()
    return {"user_count": user_count, "msg_count": msg_count}

@router.get("/api/users")
async def list_users(db: Session = Depends(get_db_session)):
    users = db.execute(select(User).order_by(User.last_seen.desc())).scalars().all()
    return [{"id": u.telegram_id, "username": u.username, "last_seen": u.last_seen} for u in users]

@router.get("/api/users/{telegram_id}", response_class=HTMLResponse)
async def user_detail(request: Request, telegram_id: int, db: Session = Depends(get_db_session)):
    user = db.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    messages = db.execute(
        select(Message).where(Message.user_id == user.id).order_by(Message.created_at.desc()).limit(50)
    ).scalars().all()
    
    return templates.TemplateResponse("user_detail.html", {
        "request": request,
        "user": user,
        "messages": messages
    })

@router.get("/api/users/{telegram_id}/export")
async def export_user(telegram_id: int, format: str = "json", db: Session = Depends(get_db_session)):
    try:
        exp_service = ExporterService(db)
        path = exp_service.export_user_messages(telegram_id, format=format)
        return FileResponse(path, filename=f"export_{telegram_id}.{format}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/users/{telegram_id}/insights")
async def generate_insights(telegram_id: int, db: Session = Depends(get_db_session)):
    ins_service = InsightService(db)
    result = ins_service.generate_user_insights(telegram_id)
    return result

@router.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
