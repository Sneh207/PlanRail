from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.section import RailwaySection


class TrafficWindow(Base):
    __tablename__ = "traffic_windows"
    __table_args__ = (
        Index("idx_traffic_win_lookup", "section_id", "hour"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    traffic_window_id: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    section_id: Mapped[str] = mapped_column(ForeignKey("railway_sections.section_id"), nullable=False, index=True)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    train_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    traffic_level: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    section: Mapped["RailwaySection"] = relationship("RailwaySection", back_populates="traffic_windows")
