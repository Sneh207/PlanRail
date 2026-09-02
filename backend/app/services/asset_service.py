from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.asset import Asset

class AssetService:
    @staticmethod
    def get_assets(
        db: Session,
        section_id: Optional[str] = None,
        department: Optional[str] = None,
        asset_type: Optional[str] = None,
        criticality: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Asset], int]:
        query = db.query(Asset)
        if section_id:
            query = query.filter(Asset.section_id == section_id)
        if department:
            query = query.filter(Asset.department == department)
        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)
        if criticality:
            query = query.filter(Asset.criticality == criticality)
            
        total = query.count()
        assets = query.order_by(Asset.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return assets, total

    @staticmethod
    def get_asset_by_id(db: Session, asset_id: str) -> Optional[Asset]:
        return db.query(Asset).filter(Asset.asset_id == asset_id).first()
