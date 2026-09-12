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
    page_size: int = Query(50, ge=1, le=500),
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

@router.patch(
    "/maintenance/{request_id}/status",
    response_model=MaintenanceRequestResponse,
    summary="Update Maintenance Task Status",
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def update_maintenance_status(
    request_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    new_status = payload.get("status")
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MISSING_STATUS", "message": "Field 'status' is required"}
        )
    try:
        updated = MaintenanceService.update_request_status(db, request_id, new_status)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": f"Maintenance Request '{request_id}' not found"}
            )
        return updated
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATUS", "message": str(val_err)}
        )

@router.post(
    "/maintenance/emergency",
    response_model=MaintenanceRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report Emergency Maintenance Defect",
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def create_emergency_maintenance(
    payload: dict,
    db: Session = Depends(get_db)
):
    section_id = payload.get("section_id")
    if not section_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MISSING_SECTION", "message": "Field 'section_id' is required"}
        )
    created = MaintenanceService.create_emergency_request(
        db,
        section_id=section_id,
        department=payload.get("department", "Engineering"),
        maintenance_type=payload.get("maintenance_type", "Emergency Defect Rectification"),
        asset_id=payload.get("asset_id"),
        asset_type=payload.get("asset_type"),
        severity=float(payload.get("severity", 5.0)),
        criticality_score=float(payload.get("criticality_score", 5.0)),
        duration_hours=float(payload.get("duration_hours", 2.0)),
        description=payload.get("description"),
        due_date=payload.get("due_date"),
    )
    return created

