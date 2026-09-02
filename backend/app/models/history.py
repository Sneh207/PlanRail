from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Float, ForeignKey, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.section import RailwaySection


class MaintenanceHistory(Base):
    __tablename__ = "maintenance_history"
    __table_args__ = (
        Index("idx_maint_hist_lookup", "asset_id", "section_id", "event_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    history_id: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.asset_id"), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(ForeignKey("railway_sections.section_id"), nullable=False, index=True)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[float] = mapped_column(Float, nullable=False)
    downtime_hours: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="maintenance_history")
    section: Mapped["RailwaySection"] = relationship("RailwaySection", back_populates="maintenance_history")
