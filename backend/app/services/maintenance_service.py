from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.maintenance import MaintenanceRequest
from app.models.history import MaintenanceHistory

class MaintenanceService:
    @staticmethod
    def get_requests(
        db: Session,
        status: Optional[str] = None,
        department: Optional[str] = None,
        section_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        criticality: Optional[str] = None,
        severity: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[MaintenanceRequest], int]:
        query = db.query(MaintenanceRequest)
        if status:
            query = query.filter(MaintenanceRequest.status == status)
        if department:
            query = query.filter(MaintenanceRequest.department == department)
        if section_id:
            query = query.filter(MaintenanceRequest.section_id == section_id)
        if asset_id:
            query = query.filter(MaintenanceRequest.asset_id == asset_id)

        total = query.count()
        requests = query.order_by(MaintenanceRequest.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return requests, total

    @staticmethod
    def get_request_by_id(db: Session, request_id: str) -> Optional[MaintenanceRequest]:
        return db.query(MaintenanceRequest).filter(
            or_(MaintenanceRequest.request_id == request_id, MaintenanceRequest.task_code == request_id)
        ).first()

    @staticmethod
    def get_history_by_asset(db: Session, asset_id: str) -> List[MaintenanceHistory]:
        return db.query(MaintenanceHistory).filter(MaintenanceHistory.asset_id == asset_id).all()
