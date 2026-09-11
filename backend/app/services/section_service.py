from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.section import RailwaySection

class SectionService:
    @staticmethod
    def get_sections(db: Session, page: int = 1, page_size: int = 20) -> Tuple[List[RailwaySection], int]:
        query = db.query(RailwaySection)
        total = query.count()
        sections = query.order_by(RailwaySection.section_id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return sections, total

    @staticmethod
    def get_section_by_id(db: Session, section_id: str) -> Optional[RailwaySection]:
        return db.query(RailwaySection).filter(
            or_(RailwaySection.section_id == section_id, RailwaySection.from_station_code == section_id)
        ).first()

