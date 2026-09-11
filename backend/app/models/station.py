from typing import Optional
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Station(Base):
    __tablename__ = "stations"

    station_id: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
    station_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    station_name: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    km_from_ndls: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    @property
    def name(self) -> str:
        return self.station_name

