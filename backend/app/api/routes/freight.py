"""
PlanRail Freight Trains API Route
=================================

Exposes read-only access to synthetic freight train planning movements for the Delhi–Agra corridor.
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.freight_service import FreightService
from app.schemas import (
    FreightTrainMovementResponse,
    PaginatedResponse,
    ErrorResponse,
)

router = APIRouter()


@router.get(
    "/freight-trains",
    response_model=PaginatedResponse[FreightTrainMovementResponse],
    summary="List Freight Train Planning Movements",
    description="Returns simulated freight train planning movements for the corridor with provenance metadata.",
    responses={500: {"model": ErrorResponse}},
)
def list_freight_trains(
    movement_date: Optional[date] = Query(None, description="Filter by scheduled movement date (YYYY-MM-DD)"),
    traffic_priority: Optional[str] = Query(None, description="Filter by traffic priority (Critical, High, Medium)"),
    commodity: Optional[str] = Query(None, description="Filter by commodity type"),
    origin_station_code: Optional[str] = Query(None, description="Filter by origin station code (e.g. NDLS, AGC)"),
    destination_station_code: Optional[str] = Query(None, description="Filter by destination station code (e.g. AGC, NDLS)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    items, total = FreightService.get_freight_movements(
        db,
        movement_date=movement_date,
        traffic_priority=traffic_priority,
        commodity=commodity,
        origin_station_code=origin_station_code,
        destination_station_code=destination_station_code,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse[FreightTrainMovementResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/freight-trains/{freight_train_id}",
    response_model=FreightTrainMovementResponse,
    summary="Get Freight Train Planning Movement by ID",
    description="Returns details and reference provenance for a specific simulated freight train planning record.",
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def get_freight_train(
    freight_train_id: str,
    db: Session = Depends(get_db),
):
    record = FreightService.get_freight_movement_by_id(db, freight_train_id=freight_train_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RESOURCE_NOT_FOUND", "message": f"Freight train record '{freight_train_id}' not found."},
        )
    return record
