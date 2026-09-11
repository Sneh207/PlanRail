import enum
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, Enum, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class BlockStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    MODIFIED = "MODIFIED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class MaintenanceWindow(Base):
    __tablename__ = "maintenance_windows"

    window_id: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
    section_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    start_hour: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[str] = mapped_column(String(20), nullable=False)
    end_time: Mapped[str] = mapped_column(String(20), nullable=False)
    expected_train_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    traffic_level: Mapped[str] = mapped_column(String(50), nullable=False)
    is_feasible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    window_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


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

    optimized_blocks: Mapped[List["OptimizedBlock"]] = relationship("OptimizedBlock", back_populates="optimization_run")


class OptimizedBlock(Base):
    __tablename__ = "optimized_blocks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    block_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    section_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    maintenance_window_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)
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

    optimization_run: Mapped[Optional["OptimizationRun"]] = relationship("OptimizationRun", back_populates="optimized_blocks")
    block_tasks: Mapped[List["BlockTask"]] = relationship("BlockTask", back_populates="optimized_block", cascade="all, delete-orphan")

    @property
    def block_id(self) -> str:
        return self.block_code

    @property
    def run_id(self) -> str:
        if self.optimization_run and self.optimization_run.run_code:
            return self.optimization_run.run_code
        return f"RUN_{self.optimization_run_id}" if self.optimization_run_id else "RUN_MANUAL"

    @property
    def duration_hours(self) -> float:
        return round(self.duration_minutes / 60.0, 2)

    @property
    def tasks(self) -> List["BlockTask"]:
        return self.block_tasks


class BlockTask(Base):
    __tablename__ = "block_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    block_id: Mapped[int] = mapped_column(ForeignKey("optimized_blocks.id"), nullable=False, index=True)
    maintenance_request_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    sequence_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    optimized_block: Mapped["OptimizedBlock"] = relationship("OptimizedBlock", back_populates="block_tasks")

    @property
    def block_task_id(self) -> str:
        return f"BT_{self.id}"

    @property
    def request_id(self) -> str:
        return str(self.maintenance_request_id)

    @property
    def sequence(self) -> int:
        return self.sequence_order

