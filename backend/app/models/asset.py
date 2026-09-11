from typing import Optional
from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Asset(Base):
    __tablename__ = "assets"

    asset_id: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
    section_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    installation_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    condition_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    criticality: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_maintenance_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    @property
    def name(self) -> str:
        return f"{self.asset_type} ({self.asset_id})"

