from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.section import RailwaySection
    from app.models.station import Station


class Train(Base):
    __tablename__ = "trains"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    train_number: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    train_name: Mapped[str] = mapped_column(String(100), nullable=False)
    train_type: Mapped[str] = mapped_column(String(50), nullable=False)
    origin_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    destination_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    service_pattern: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_synthetic_schedule: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    schedules: Mapped[List["TrainSchedule"]] = relationship("TrainSchedule", back_populates="train")
    train_movements: Mapped[List["TrainMovement"]] = relationship("TrainMovement", back_populates="train")


class TrainSchedule(Base):
    __tablename__ = "train_schedules"
    __table_args__ = (
        Index("idx_train_sched_lookup", "train_number", "station_code", "sequence"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    train_number: Mapped[str] = mapped_column(ForeignKey("trains.train_number"), nullable=False, index=True)
    station_code: Mapped[str] = mapped_column(ForeignKey("stations.station_code"), nullable=False, index=True)
    station_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    arrival_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    departure_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    day: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    km_from_origin: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    train: Mapped["Train"] = relationship("Train", back_populates="schedules")
    station: Mapped["Station"] = relationship("Station", back_populates="schedules")


class TrainMovement(Base):
    __tablename__ = "train_movements"
    __table_args__ = (
        Index("idx_train_mov_window", "section_id", "scheduled_arrival", "scheduled_departure"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    train_id: Mapped[int] = mapped_column(ForeignKey("trains.id"), nullable=False, index=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("railway_sections.id"), nullable=False, index=True)
    scheduled_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_departure: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_arrival: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_departure: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delay_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    direction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), default="SCHEDULED", nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    train: Mapped["Train"] = relationship("Train", back_populates="train_movements")
    section: Mapped["RailwaySection"] = relationship("RailwaySection", back_populates="train_movements")
