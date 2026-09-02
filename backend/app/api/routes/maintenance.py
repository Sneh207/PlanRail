from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.maintenance_service import MaintenanceService
from app.schemas import (
    MaintenanceRequestResponse,
    MaintenanceRequestDetailResponse,
    PaginatedResponse,
    ErrorResponse
)

router = APIRouter()

@router.get(
    "/maintenance",
    response_model=PaginatedResponse[MaintenanceRequestResponse],
    summary="List Maintenance Requests",
    responses={500: {"model": ErrorResponse}}
)
def list_maintenance_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    department: Optional[str] = Query(None),
    section_id: Optional[str] = Query(None),
    asset_id: Optional[str] = Query(None),
    criticality: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items, total = MaintenanceService.get_requests(
        db,
        status=status_filter,
        department=department,
        section_id=section_id,
        asset_id=asset_id,
        criticality=criticality,
        severity=severity,
        page=page,
        page_size=page_size
    )
    return PaginatedResponse[MaintenanceRequestResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

@router.get(
    "/maintenance/{request_id}",
    response_model=MaintenanceRequestDetailResponse,
    summary="Get Maintenance Request Detail",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def get_maintenance_request(request_id: str, db: Session = Depends(get_db)):
    req = MaintenanceService.get_request_by_id(db, request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RESOURCE_NOT_FOUND", "message": f"Maintenance Request '{request_id}' not found"}
        )
    history = MaintenanceService.get_history_by_asset(db, req.asset_id)
    
    req_dict = MaintenanceRequestResponse.model_validate(req).model_dump()
    req_dict["history"] = history
    return req_dict
