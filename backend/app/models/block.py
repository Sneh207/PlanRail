import enum
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, Enum, UniqueConstraint, Index, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.section import RailwaySection
    from app.models.maintenance import MaintenanceRequest


class BlockStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    MODIFIED = "MODIFIED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class MaintenanceWindow(Base):
    __tablename__ = "maintenance_windows"
    __table_args__ = (
        Index("idx_maint_win_lookup", "section_id", "start_hour", "is_feasible"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    window_id: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    section_id: Mapped[str] = mapped_column(ForeignKey("railway_sections.section_id"), nullable=False, index=True)
    start_hour: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[str] = mapped_column(String(20), nullable=False)
    end_time: Mapped[str] = mapped_column(String(20), nullable=False)
    expected_train_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    traffic_level: Mapped[str] = mapped_column(String(50), nullable=False)
    is_feasible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    window_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    section: Mapped["RailwaySection"] = relationship("RailwaySection", back_populates="maintenance_windows")
    optimized_blocks: Mapped[List["OptimizedBlock"]] = relationship("OptimizedBlock", back_populates="maintenance_window")


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="SUCCESS", nullable=False)
    objective: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    optimized_blocks: Mapped[List["OptimizedBlock"]] = relationship("OptimizedBlock", back_populates="optimization_run")


class OptimizedBlock(Base):
    __tablename__ = "optimized_blocks"
    __table_args__ = (
        Index("idx_opt_block_lookup", "section_id", "status", "start_time"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    block_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    section_id: Mapped[int] = mapped_column(ForeignKey("railway_sections.id"), nullable=False, index=True)
    maintenance_window_id: Mapped[Optional[int]] = mapped_column(ForeignKey("maintenance_windows.id"), nullable=True, index=True)
    optimization_run_id: Mapped[Optional[int]] = mapped_column(ForeignKey("optimization_runs.id"), nullable=True, index=True)
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[BlockStatus] = mapped_column(Enum(BlockStatus), default=BlockStatus.PROPOSED, index=True, nullable=False)
    optimization_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    section: Mapped["RailwaySection"] = relationship("RailwaySection", back_populates="optimized_blocks")
    maintenance_window: Mapped[Optional["MaintenanceWindow"]] = relationship("MaintenanceWindow", back_populates="optimized_blocks")
    optimization_run: Mapped[Optional["OptimizationRun"]] = relationship("OptimizationRun", back_populates="optimized_blocks")
    block_tasks: Mapped[List["BlockTask"]] = relationship("BlockTask", back_populates="optimized_block", cascade="all, delete-orphan")


class BlockTask(Base):
    __tablename__ = "block_tasks"
    __table_args__ = (
        UniqueConstraint("block_id", "maintenance_request_id", name="uq_block_maintenance_request"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    block_id: Mapped[int] = mapped_column(ForeignKey("optimized_blocks.id"), nullable=False, index=True)
    maintenance_request_id: Mapped[int] = mapped_column(ForeignKey("maintenance_requests.id"), nullable=False, index=True)
    sequence_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    optimized_block: Mapped["OptimizedBlock"] = relationship("OptimizedBlock", back_populates="block_tasks")
    maintenance_request: Mapped["MaintenanceRequest"] = relationship("MaintenanceRequest", back_populates="block_tasks")
