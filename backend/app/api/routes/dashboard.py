from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas import DashboardResponse, ErrorResponse

router = APIRouter()

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Get Controller Dashboard Data",
    responses={500: {"model": ErrorResponse}}
)
def get_dashboard(db: Session = Depends(get_db)):
    metrics = DashboardService.get_dashboard_metrics(db)
    return metrics
