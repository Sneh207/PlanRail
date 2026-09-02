"""
SQLAlchemy Engine, SessionFactory, and FastAPI dependency module.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

engine = None
SessionLocal = None

if settings.DATABASE_URL:
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a transactional SQLAlchemy database session.
    """
    if SessionLocal is None:
        raise RuntimeError("Database connection URL (DATABASE_URL) is not configured.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
