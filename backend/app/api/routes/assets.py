from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.asset_service import AssetService
from app.schemas import AssetResponse, PaginatedResponse, ErrorResponse

router = APIRouter()

@router.get(
    "/assets",
    response_model=PaginatedResponse[AssetResponse],
    summary="List Track Assets",
    responses={500: {"model": ErrorResponse}}
)
def list_assets(
    section_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    asset_type: Optional[str] = Query(None),
    criticality: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items, total = AssetService.get_assets(
        db,
        section_id=section_id,
        department=department,
        asset_type=asset_type,
        criticality=criticality,
        page=page,
        page_size=page_size
    )
    return PaginatedResponse[AssetResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

@router.get(
    "/assets/{asset_id}",
    response_model=AssetResponse,
    summary="Get Asset Detail",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = AssetService.get_asset_by_id(db, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RESOURCE_NOT_FOUND", "message": f"Asset '{asset_id}' not found"}
        )
    return asset
