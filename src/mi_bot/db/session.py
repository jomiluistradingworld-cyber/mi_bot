from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.mi_bot.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    echo=False, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Dependency for FastAPI to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    from src.mi_bot.db.models import Base
    Base.metadata.create_all(bind=engine)
