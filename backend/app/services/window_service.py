from typing import List, Tuple, Optional
from datetime import time
from sqlalchemy.orm import Session
from app.models.block import MaintenanceWindow
from app.models.traffic import TrafficWindow

class WindowService:
    @staticmethod
    def get_maintenance_windows(
        db: Session,
        section_id: Optional[str] = None,
        hour: Optional[int] = None,
        traffic_level: Optional[str] = None,
        is_feasible: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[dict], int]:
        query = db.query(MaintenanceWindow)
        if section_id:
            query = query.filter(MaintenanceWindow.section_id == section_id)
        if hour is not None:
            query = query.filter(MaintenanceWindow.start_hour == hour)
        if traffic_level:
            query = query.filter(MaintenanceWindow.traffic_level == traffic_level)
        if is_feasible is not None:
            query = query.filter(MaintenanceWindow.is_feasible == is_feasible)

        total = query.count()
        windows = query.order_by(MaintenanceWindow.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        
        results = []
        for w in windows:
            start_t = None
            if w.start_time:
                parts = [int(p) for p in w.start_time.split(":")]
                start_t = time(parts[0], parts[1], parts[2] if len(parts) > 2 else 0)
            end_t = None
            if w.end_time:
                parts = [int(p) for p in w.end_time.split(":")]
                end_t = time(parts[0], parts[1], parts[2] if len(parts) > 2 else 0)
            
            results.append({
                "window_id": w.window_id,
                "section_id": w.section_id,
                "start_hour": w.start_hour,
                "start_time": start_t,
                "end_time": end_t,
                "expected_train_count": w.expected_train_count,
                "traffic_level": w.traffic_level,
                "is_feasible": w.is_feasible,
                "window_reason": w.window_reason,
            })
        return results, total

    @staticmethod
    def get_traffic_windows(
        db: Session,
        section_id: Optional[str] = None,
        hour: Optional[int] = None,
        traffic_level: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[TrafficWindow], int]:
        query = db.query(TrafficWindow)
        if section_id:
            query = query.filter(TrafficWindow.section_id == section_id)
        if hour is not None:
            query = query.filter(TrafficWindow.hour == hour)
        if traffic_level:
            query = query.filter(TrafficWindow.traffic_level == traffic_level)

        total = query.count()
        tw = query.order_by(TrafficWindow.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return tw, total
