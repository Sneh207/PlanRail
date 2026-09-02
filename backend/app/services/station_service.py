from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.models.station import Station

class StationService:
    @staticmethod
    def get_stations(
        db: Session, page: int = 1, page_size: int = 20, search: Optional[str] = None
    ) -> Tuple[List[Station], int]:
        query = db.query(Station)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Station.station_code.ilike(search_pattern),
                    Station.name.ilike(search_pattern)
                )
            )
        total = query.count()
        stations = query.order_by(Station.km_from_ndls.asc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # Map internal 'name' field to 'station_name' schema compatibility
        for s in stations:
            if not getattr(s, 'station_name', None):
                setattr(s, 'station_name', s.name)
        return stations, total

    @staticmethod
    def get_station_by_id(db: Session, station_id: str) -> Optional[Station]:
        station = db.query(Station).filter(
            or_(Station.station_id == station_id, Station.station_code == station_id)
        ).first()
        if station and not getattr(station, 'station_name', None):
            setattr(station, 'station_name', station.name)
        return station
