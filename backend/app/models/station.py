from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.section import RailwaySection
    from app.models.asset import Asset
    from app.models.train import TrainSchedule


class Station(Base):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    station_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    station_name: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    km_from_ndls: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )
    zone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    division: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    start_sections: Mapped[List["RailwaySection"]] = relationship(
        "RailwaySection", foreign_keys="RailwaySection.from_station_code", back_populates="from_station"
    )
    end_sections: Mapped[List["RailwaySection"]] = relationship(
        "RailwaySection", foreign_keys="RailwaySection.to_station_code", back_populates="to_station"
    )
    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="station")
    schedules: Mapped[List["TrainSchedule"]] = relationship("TrainSchedule", back_populates="station")
