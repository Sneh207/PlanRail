from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.maintenance import MaintenanceRequest
from app.models.block import MaintenanceWindow, OptimizationRun
from app.models.train import Train

class DashboardService:
    @staticmethod
    def get_dashboard_metrics(db: Session) -> dict:
        total_requests = db.query(func.count(MaintenanceRequest.request_id)).scalar() or 0
        pending_requests = db.query(func.count(MaintenanceRequest.request_id)).filter(MaintenanceRequest.status == "PENDING").scalar() or 0
        
        # Filter critical/high based on severity numeric threshold (>= 70)
        critical_high_requests = db.query(func.count(MaintenanceRequest.request_id)).filter(
            MaintenanceRequest.severity >= 70.0
        ).scalar() or 0
        
        overdue_requests = db.query(func.count(MaintenanceRequest.request_id)).filter(MaintenanceRequest.overdue_days > 0).scalar() or 0
        
        available_windows = db.query(func.count(MaintenanceWindow.window_id)).filter(MaintenanceWindow.is_feasible == True).scalar() or 0
        total_trains = db.query(func.count(Train.train_number)).scalar() or 0
        
        latest_opt = db.query(OptimizationRun).order_by(OptimizationRun.created_at.desc()).first()
        latest_opt_dict = None
        if latest_opt:
            latest_opt_dict = {
                "run_id": latest_opt.run_code,
                "status": latest_opt.status,
                "created_at": latest_opt.created_at
            }
            
        return {
            "total_maintenance_requests": total_requests,
            "pending_requests": pending_requests,
            "critical_high_requests": critical_high_requests,
            "overdue_requests": overdue_requests,
            "available_maintenance_windows": available_windows,
            "total_trains": total_trains,
            "latest_optimization": latest_opt_dict
        }

