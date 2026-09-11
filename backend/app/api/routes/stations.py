from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.station_service import StationService
from app.schemas import StationResponse, PaginatedResponse, ErrorResponse

router = APIRouter()

@router.get(
    "/stations",
    response_model=PaginatedResponse[StationResponse],
    summary="List Railway Stations",
    responses={500: {"model": ErrorResponse}}
)
def list_stations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    items, total = StationService.get_stations(db, page=page, page_size=page_size, search=search)
    return PaginatedResponse[StationResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

@router.get(
    "/stations/{station_id}",
    response_model=StationResponse,
    summary="Get Station Detail",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def get_station(station_id: str, db: Session = Depends(get_db)):
    station = StationService.get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RESOURCE_NOT_FOUND", "message": f"Station '{station_id}' not found"}
        )
    return station
