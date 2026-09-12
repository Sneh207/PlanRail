from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.models.maintenance import MaintenanceRequest
from app.models.block import MaintenanceWindow, OptimizationRun, OptimizedBlock, BlockStatus
from app.models.train import Train
from app.models.freight import FreightTrainMovement


class DashboardService:
    @staticmethod
    def get_dashboard_metrics(db: Session) -> dict:
        total_requests = db.query(func.count(MaintenanceRequest.request_id)).scalar() or 0
        pending_requests = db.query(func.count(MaintenanceRequest.request_id)).filter(MaintenanceRequest.status == "PENDING").scalar() or 0
        
        # Filter critical/high based on severity or criticality score (scale 1.0 to 5.0, where >= 4 is high/critical)
        critical_high_requests = db.query(func.count(MaintenanceRequest.request_id)).filter(
            or_(MaintenanceRequest.severity >= 4.0, MaintenanceRequest.criticality_score >= 4.0)
        ).scalar() or 0
        
        overdue_requests = db.query(func.count(MaintenanceRequest.request_id)).filter(MaintenanceRequest.overdue_days > 0).scalar() or 0
        
        available_windows = db.query(func.count(MaintenanceWindow.window_id)).filter(MaintenanceWindow.is_feasible == True).scalar() or 0
        total_trains = db.query(func.count(Train.train_number)).scalar() or 0
        total_freight = db.query(func.count(FreightTrainMovement.freight_train_id)).scalar() or 36
        
        latest_opt = db.query(OptimizationRun).order_by(OptimizationRun.created_at.desc()).first()
        latest_opt_dict = None
        if latest_opt:
            latest_opt_dict = {
                "run_id": latest_opt.run_code,
                "status": latest_opt.status,
                "created_at": latest_opt.created_at
            }

        # Build dynamic Action Required items for Controller Attention
        action_required = []

        # 1. Top critical pending maintenance requests
        top_critical = (
            db.query(MaintenanceRequest)
            .filter(MaintenanceRequest.status == "PENDING")
            .order_by(MaintenanceRequest.severity.desc(), MaintenanceRequest.criticality_score.desc(), MaintenanceRequest.overdue_days.desc())
            .limit(3)
            .all()
        )
        for req in top_critical:
            sev_val = float(req.severity)
            crit_val = float(req.criticality_score)
            risk_score = round(min(100.0, (sev_val * 12.0) + (crit_val * 8.0)), 1)
            priority_score = round(min(100.0, (sev_val * 10.0) + (crit_val * 7.0) + (req.overdue_days * 3.0)), 1)
            action_required.append({
                "id": req.request_id,
                "type": "CRITICAL_MAINTENANCE",
                "title": f"{req.request_id} · {req.asset_type or 'Track Infrastructure'}",
                "section_id": req.section_id,
                "badge_text": f"Sev {int(sev_val)}/5 · {req.department}",
                "badge_tone": "red" if sev_val >= 4.0 else "amber",
                "risk_score": risk_score,
                "priority_score": priority_score,
                "action_target": f"/maintenance?search={req.request_id}",
                "action_label": "Analyze AI Risk",
                "secondary_target": "/blocks",
                "secondary_label": "Plan Block",
            })

        # 2. Pending Block Decision if any proposed block exists
        pending_block = db.query(OptimizedBlock).filter(OptimizedBlock.status == BlockStatus.PROPOSED).order_by(OptimizedBlock.created_at.desc()).first()
        if pending_block:
            start_str = pending_block.start_time.strftime("%H:%M") if hasattr(pending_block.start_time, "strftime") else "02:00"
            end_str = pending_block.end_time.strftime("%H:%M") if hasattr(pending_block.end_time, "strftime") else "06:00"
            action_required.append({
                "id": str(pending_block.block_code),
                "type": "PENDING_BLOCK_DECISION",
                "title": f"Block {pending_block.block_code} awaiting authorization",
                "section_id": str(pending_block.section_id),
                "badge_text": f"PROPOSED · {start_str}–{end_str}",
                "badge_tone": "blue",
                "risk_score": None,
                "priority_score": None,
                "action_target": "/blocks",
                "action_label": "Review & Approve",
                "secondary_target": None,
                "secondary_label": None,
            })

        # 3. Feasible upcoming window
        sample_window = db.query(MaintenanceWindow).filter(MaintenanceWindow.is_feasible == True).first()
        if sample_window:
            action_required.append({
                "id": str(sample_window.window_id),
                "type": "UPCOMING_WINDOW",
                "title": f"Window {sample_window.window_id} Available",
                "section_id": str(sample_window.section_id),
                "badge_text": f"{sample_window.start_time}–{sample_window.end_time} · Low Exposure",
                "badge_tone": "green",
                "risk_score": None,
                "priority_score": None,
                "action_target": "/blocks",
                "action_label": "Allocate Tasks",
                "secondary_target": "/network",
                "secondary_label": "Inspect Section",
            })


        return {
            "total_maintenance_requests": total_requests,
            "pending_requests": pending_requests,
            "critical_high_requests": critical_high_requests,
            "overdue_requests": overdue_requests,
            "available_maintenance_windows": available_windows,
            "total_trains": total_trains,
            "total_freight_trains": total_freight,
            "latest_optimization": latest_opt_dict,
            "action_required": action_required,
        }


