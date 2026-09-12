from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.block_service import BlockService
from app.schemas import OptimizedBlockResponse, PaginatedResponse, ErrorResponse

router = APIRouter()

@router.get(
    "/blocks",
    response_model=PaginatedResponse[OptimizedBlockResponse],
    summary="List Optimized Blocks",
    responses={500: {"model": ErrorResponse}}
)
def list_blocks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items, total = BlockService.get_blocks(db, page=page, page_size=page_size)
    return PaginatedResponse[OptimizedBlockResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

@router.get(
    "/blocks/{block_id}",
    response_model=OptimizedBlockResponse,
    summary="Get Block Detail",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def get_block(block_id: str, db: Session = Depends(get_db)):
    block = BlockService.get_block_by_id(db, block_id)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RESOURCE_NOT_FOUND", "message": f"Optimized Block '{block_id}' not found"}
        )
    return block

@router.patch(
    "/blocks/{block_id}/status",
    response_model=OptimizedBlockResponse,
    summary="Update Block Status (Approve/Reject/Modify)",
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def update_block_status(
    block_id: str,
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
        updated = BlockService.update_block_status(db, block_id, new_status)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": f"Optimized Block '{block_id}' not found"}
            )
        return updated
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATUS", "message": str(val_err)}
        )

