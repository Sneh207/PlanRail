"""
SQLAlchemy Engine, SessionFactory, and FastAPI dependency module.
"""
import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

logger = logging.getLogger(__name__)

engine = None
SessionLocal = None

if settings.DATABASE_URL:
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    if db_url.startswith("sqlite"):
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
        )
    else:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=300,
        )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Safely initialize application tables (e.g. optimization_runs, optimized_blocks,
    block_tasks, simulation_runs) without destroying or dropping existing dataset tables.
    Also creates the maintenance_compatibility SQL view if task_compatibility table exists.
    """
    if engine is None:
        logger.warning("Database engine is not initialized; skipping init_db.")
        return

    from app.database.base import Base
    import app.models  # noqa: F401 - Register all models with Base.metadata

    # Create only missing application tables
    Base.metadata.create_all(bind=engine)

    # If SQLite has task_compatibility table, ensure maintenance_compatibility view exists
    try:
        with engine.connect() as conn:
            if engine.dialect.name == "sqlite":
                conn.execute(text(
                    "CREATE VIEW IF NOT EXISTS maintenance_compatibility AS "
                    "SELECT ROW_NUMBER() OVER () as id, department_a, department_b, compatibility, "
                    "NULL as reason, datetime('now') as created_at FROM task_compatibility"
                ))
                conn.commit()
    except Exception as e:
        logger.debug("Database compatibility view setup note: %s", e)

    # Idempotent seeding of simulated freight dataset
    try:
        from app.database.freight_loader import import_freight_dataset
        with SessionLocal() as db_session:
            inserted, total = import_freight_dataset(db_session)
            if inserted > 0:
                logger.info("Loaded %d new freight train planning movements (Total: %d).", inserted, total)
    except Exception as e:
        logger.warning("Freight dataset seeding note: %s", e)


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

