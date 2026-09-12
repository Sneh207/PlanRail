from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.admin_service import AdminService
from app.schemas import AdminConfigResponse, AdminConfigUpdateRequest, ErrorResponse

router = APIRouter()


@router.get(
    "/admin/health",
    summary="Comprehensive Admin System Health & Status Diagnostics",
    responses={500: {"model": ErrorResponse}},
)
def get_admin_health(db: Session = Depends(get_db)):
    return AdminService.get_system_health(db)


@router.get(
    "/admin/config",
    response_model=AdminConfigResponse,
    summary="Get Operational Corridor & Solver Configuration",
    responses={500: {"model": ErrorResponse}},
)
def get_admin_config(db: Session = Depends(get_db)):
    return AdminService.get_or_create_config(db)


@router.post(
    "/admin/config",
    response_model=AdminConfigResponse,
    summary="Update Operational Corridor & Solver Configuration",
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def update_admin_config(
    payload: AdminConfigUpdateRequest,
    db: Session = Depends(get_db),
):
    update_dict = payload.model_dump(exclude_unset=True)
    updated = AdminService.update_config(db, update_dict)
    return updated
