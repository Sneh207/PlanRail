from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.train_service import TrainService
from app.schemas import (
    TrainResponse,
    TrainScheduleResponse,
    PaginatedResponse,
    ErrorResponse
)

router = APIRouter()

@router.get(
    "/trains",
    response_model=PaginatedResponse[TrainResponse],
    summary="List Corridor Trains",
    responses={500: {"model": ErrorResponse}}
)
def list_trains(
    train_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items, total = TrainService.get_trains(db, page=page, page_size=page_size, train_type=train_type)
    return PaginatedResponse[TrainResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

@router.get(
    "/trains/{train_number}",
    response_model=TrainResponse,
    summary="Get Train Detail",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def get_train(train_number: str, db: Session = Depends(get_db)):
    train = TrainService.get_train_by_number(db, train_number)
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RESOURCE_NOT_FOUND", "message": f"Train '{train_number}' not found"}
        )
    return train

@router.get(
    "/trains/{train_number}/schedule",
    response_model=List[TrainScheduleResponse],
    summary="Get Train Schedule",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def get_train_schedule(train_number: str, db: Session = Depends(get_db)):
    train = TrainService.get_train_by_number(db, train_number)
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RESOURCE_NOT_FOUND", "message": f"Train '{train_number}' not found"}
        )
    schedule = TrainService.get_train_schedule(db, train_number)
    return schedule
