from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.section import RailwaySection

class SectionService:
    @staticmethod
    def get_sections(db: Session, page: int = 1, page_size: int = 20) -> Tuple[List[RailwaySection], int]:
        query = db.query(RailwaySection)
        total = query.count()
        sections = query.order_by(RailwaySection.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        # Convert WKB geometry to string if present, or set None
        for sec in sections:
            if sec.geometry is not None:
                sec.geometry = str(sec.geometry)
        return sections, total

    @staticmethod
    def get_section_by_id(db: Session, section_id: str) -> Optional[RailwaySection]:
        sec = db.query(RailwaySection).filter(
            or_(RailwaySection.section_id == section_id, RailwaySection.section_code == section_id)
        ).first()
        if sec and sec.geometry is not None:
            sec.geometry = str(sec.geometry)
        return sec
