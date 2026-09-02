from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.section import RailwaySection
    from app.models.station import Station
    from app.models.maintenance import MaintenanceRequest
    from app.models.history import MaintenanceHistory


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    asset_code: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    section_id: Mapped[str] = mapped_column(ForeignKey("railway_sections.section_id"), nullable=False, index=True)
    station_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stations.id"), nullable=True, index=True)
    
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    installation_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    condition_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    criticality: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )
    last_maintenance_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    section: Mapped["RailwaySection"] = relationship("RailwaySection", back_populates="assets")
    station: Mapped[Optional["Station"]] = relationship("Station", back_populates="assets")
    maintenance_requests: Mapped[List["MaintenanceRequest"]] = relationship("MaintenanceRequest", back_populates="asset")
    maintenance_history: Mapped[List["MaintenanceHistory"]] = relationship("MaintenanceHistory", back_populates="asset")
