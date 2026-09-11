from typing import Optional
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class RailwaySection(Base):
    __tablename__ = "railway_sections"

    section_id: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
    from_station_code: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    to_station_code: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    from_station_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    to_station_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    track_configuration: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    electrification: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    traffic_class: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    @property
    def section_code(self) -> str:
        return self.section_id

    @property
    def name(self) -> str:
        from_name = self.from_station_name or self.from_station_code
        to_name = self.to_station_name or self.to_station_code
        return f"{from_name} — {to_name}"

