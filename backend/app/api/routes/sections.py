from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.section_service import SectionService
from app.schemas import SectionResponse, PaginatedResponse, ErrorResponse

router = APIRouter()

@router.get(
    "/sections",
    response_model=PaginatedResponse[SectionResponse],
    summary="List Railway Sections",
    responses={500: {"model": ErrorResponse}}
)
def list_sections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items, total = SectionService.get_sections(db, page=page, page_size=page_size)
    return PaginatedResponse[SectionResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

@router.get(
    "/sections/{section_id}",
    response_model=SectionResponse,
    summary="Get Section Detail",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
def get_section(section_id: str, db: Session = Depends(get_db)):
    section = SectionService.get_section_by_id(db, section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RESOURCE_NOT_FOUND", "message": f"Railway Section '{section_id}' not found"}
        )
    return section
