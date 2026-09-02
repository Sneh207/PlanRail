from typing import List, Tuple, Optional
from datetime import datetime, time
from sqlalchemy.orm import Session
from app.models.train import Train, TrainSchedule

class TrainService:
    @staticmethod
    def get_trains(
        db: Session, page: int = 1, page_size: int = 20, train_type: Optional[str] = None
    ) -> Tuple[List[Train], int]:
        query = db.query(Train)
        if train_type:
            query = query.filter(Train.train_type == train_type)
        total = query.count()
        trains = query.order_by(Train.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return trains, total

    @staticmethod
    def get_train_by_number(db: Session, train_number: str) -> Optional[Train]:
        return db.query(Train).filter(Train.train_number == train_number).first()

    @staticmethod
    def get_train_schedule(db: Session, train_number: str) -> List[dict]:
        schedules = (
            db.query(TrainSchedule)
            .filter(TrainSchedule.train_number == train_number)
            .order_by(TrainSchedule.sequence.asc())
            .all()
        )
        results = []
        for s in schedules:
            arr_time = None
            if s.arrival_time:
                try:
                    parts = [int(p) for p in s.arrival_time.split(":")]
                    arr_time = time(parts[0], parts[1], parts[2] if len(parts) > 2 else 0)
                except Exception:
                    arr_time = None
            dep_time = None
            if s.departure_time:
                try:
                    parts = [int(p) for p in s.departure_time.split(":")]
                    dep_time = time(parts[0], parts[1], parts[2] if len(parts) > 2 else 0)
                except Exception:
                    dep_time = None

            results.append({
                "schedule_id": s.schedule_id,
                "train_number": s.train_number,
                "station_code": s.station_code,
                "station_name": s.station_name,
                "arrival_time": arr_time,
                "departure_time": dep_time,
                "day_number": s.day,
                "sequence": s.sequence,
            })
        return results
