from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.window_service import WindowService
from app.schemas import (
    MaintenanceWindowResponse,
    TrafficWindowResponse,
    PaginatedResponse,
    ErrorResponse
)

router = APIRouter()

@router.get(
    "/maintenance-windows",
    response_model=PaginatedResponse[MaintenanceWindowResponse],
    summary="List Maintenance Windows",
    responses={500: {"model": ErrorResponse}}
)
def list_maintenance_windows(
    section_id: Optional[str] = Query(None),
    hour: Optional[int] = Query(None, ge=0, le=23),
    traffic_level: Optional[str] = Query(None),
    is_feasible: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items, total = WindowService.get_maintenance_windows(
        db,
        section_id=section_id,
        hour=hour,
        traffic_level=traffic_level,
        is_feasible=is_feasible,
        page=page,
        page_size=page_size
    )
    return PaginatedResponse[MaintenanceWindowResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

@router.get(
    "/traffic-windows",
    response_model=PaginatedResponse[TrafficWindowResponse],
    summary="List Traffic Density Windows",
    responses={500: {"model": ErrorResponse}}
)
def list_traffic_windows(
    section_id: Optional[str] = Query(None),
    hour: Optional[int] = Query(None, ge=0, le=23),
    traffic_level: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items, total = WindowService.get_traffic_windows(
        db,
        section_id=section_id,
        hour=hour,
        traffic_level=traffic_level,
        page=page,
        page_size=page_size
    )
    return PaginatedResponse[TrafficWindowResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )
