from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.station import Station
    from app.models.asset import Asset
    from app.models.maintenance import MaintenanceRequest
    from app.models.history import MaintenanceHistory
    from app.models.train import TrainMovement
    from app.models.traffic import TrafficWindow
    from app.models.block import MaintenanceWindow, OptimizedBlock


class RailwaySection(Base):
    __tablename__ = "railway_sections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    section_id: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    section_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    from_station_code: Mapped[str] = mapped_column(ForeignKey("stations.station_code"), nullable=False, index=True)
    to_station_code: Mapped[str] = mapped_column(ForeignKey("stations.station_code"), nullable=False, index=True)
    from_station_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    to_station_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    track_configuration: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    electrification: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    traffic_class: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    geometry: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="LINESTRING", srid=4326), nullable=True
    )
    traffic_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    from_station: Mapped["Station"] = relationship("Station", foreign_keys=[from_station_code], back_populates="start_sections")
    to_station: Mapped["Station"] = relationship("Station", foreign_keys=[to_station_code], back_populates="end_sections")
    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="section")
    maintenance_requests: Mapped[List["MaintenanceRequest"]] = relationship("MaintenanceRequest", back_populates="section")
    maintenance_history: Mapped[List["MaintenanceHistory"]] = relationship("MaintenanceHistory", back_populates="section")
    train_movements: Mapped[List["TrainMovement"]] = relationship("TrainMovement", back_populates="section")
    traffic_windows: Mapped[List["TrafficWindow"]] = relationship("TrafficWindow", back_populates="section")
    maintenance_windows: Mapped[List["MaintenanceWindow"]] = relationship("MaintenanceWindow", back_populates="section")
    optimized_blocks: Mapped[List["OptimizedBlock"]] = relationship("OptimizedBlock", back_populates="section")
