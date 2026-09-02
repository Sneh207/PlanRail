from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()


@router.get("/health", summary="Health Check")
def health_check():
    return {"status": "ok"}


@router.get("/health/db", summary="Database Health Check")
def db_health_check(db: Session = Depends(get_db)):
    try:
        # Check database connectivity
        db.execute(text("SELECT 1;"))

        # Check PostGIS extension status
        postgis_count = db.execute(
            text("SELECT count(*) FROM pg_extension WHERE extname = 'postgis';")
        ).scalar()
        postgis_available = bool(postgis_count and postgis_count > 0)

        return {
            "status": "ok",
            "database": "connected",
            "postgis": postgis_available
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )
