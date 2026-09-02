from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.section import RailwaySection
    from app.models.block import BlockTask


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    __table_args__ = (
        Index("idx_maint_req_search", "section_id", "status", "due_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    task_code: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.asset_id"), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(ForeignKey("railway_sections.section_id"), nullable=False, index=True)
    
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    maintenance_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    severity: Mapped[float] = mapped_column(Float, nullable=False)
    criticality_score: Mapped[float] = mapped_column(Float, nullable=False)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    overdue_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    baseline_risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True, nullable=False)
    
    # Optional AI output scores
    priority_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    traffic_impact_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    crew_required: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="maintenance_requests")
    section: Mapped["RailwaySection"] = relationship("RailwaySection", back_populates="maintenance_requests")
    block_tasks: Mapped[List["BlockTask"]] = relationship("BlockTask", back_populates="maintenance_request")
