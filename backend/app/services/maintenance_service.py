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
        if severity:
            try:
                query = query.filter(MaintenanceRequest.severity == float(severity))
            except (ValueError, TypeError):
                pass
        if criticality:
            try:
                query = query.filter(MaintenanceRequest.criticality_score == float(criticality))
            except (ValueError, TypeError):
                pass

        total = query.count()
        requests = query.order_by(MaintenanceRequest.due_date.asc(), MaintenanceRequest.request_id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return requests, total

    @staticmethod
    def get_request_by_id(db: Session, request_id: str) -> Optional[MaintenanceRequest]:
        return db.query(MaintenanceRequest).filter(MaintenanceRequest.request_id == request_id).first()

    @staticmethod
    def get_history_by_asset(db: Session, asset_id: str) -> List[MaintenanceHistory]:
        return db.query(MaintenanceHistory).filter(MaintenanceHistory.asset_id == asset_id).order_by(MaintenanceHistory.event_date.desc()).all()

    @staticmethod
    def update_request_status(db: Session, request_id: str, new_status: str) -> Optional[MaintenanceRequest]:
        req = db.query(MaintenanceRequest).filter(MaintenanceRequest.request_id == request_id).first()
        if not req:
            return None
        valid_statuses = {"PENDING", "ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED"}
        clean_status = new_status.strip().upper()
        if clean_status not in valid_statuses:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: {valid_statuses}")
        
        valid_transitions = {
            "PENDING": {"ACCEPTED", "CANCELLED"},
            "ACCEPTED": {"IN_PROGRESS", "CANCELLED"},
            "IN_PROGRESS": {"COMPLETED", "CANCELLED"},
            "COMPLETED": set(),
            "CANCELLED": set(),
        }
        
        current = (req.status or "PENDING").strip().upper()
        if current == clean_status:
            return req
            
        allowed = valid_transitions.get(current, set())
        if clean_status not in allowed and clean_status != "PENDING":
            raise ValueError(f"Cannot transition task from '{current}' to '{clean_status}'. Valid next states: {allowed}")

        req.status = clean_status
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def create_emergency_request(
        db: Session,
        section_id: str,
        department: str = "Engineering",
        maintenance_type: str = "Emergency Repair",
        asset_id: Optional[str] = None,
        asset_type: Optional[str] = None,
        severity: float = 5.0,
        criticality_score: float = 5.0,
        duration_hours: float = 2.0,
        description: Optional[str] = None,
        due_date: Optional[any] = None,
    ) -> MaintenanceRequest:
        from datetime import date as dt_date
        count = db.query(MaintenanceRequest).count()
        req_id = f"EMG{count + 1:04d}"
        if not asset_id:
            from app.models.asset import Asset
            asset = db.query(Asset).filter(Asset.section_id == section_id, Asset.department == department).first()
            if not asset:
                asset = db.query(Asset).filter(Asset.section_id == section_id).first()
            asset_id = asset.asset_id if asset else f"AST_{section_id}_01"
            if not asset_type and asset:
                asset_type = asset.asset_type

        target_due = due_date.isoformat() if hasattr(due_date, "isoformat") else str(due_date or dt_date.today().isoformat())
        new_req = MaintenanceRequest(
            request_id=req_id,
            asset_id=asset_id,
            section_id=section_id,
            department=department,
            asset_type=asset_type or "Track / Permanent Way",
            maintenance_type=maintenance_type,
            severity=severity,
            criticality_score=criticality_score,
            duration_hours=duration_hours,
            created_date=dt_date.today().isoformat(),
            due_date=target_due,
            overdue_days=0,
            baseline_risk_score=95.0,
            status="PENDING",
        )
        db.add(new_req)
        db.commit()
        db.refresh(new_req)
        return new_req

