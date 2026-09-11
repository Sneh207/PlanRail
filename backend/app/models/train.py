from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Train(Base):
    __tablename__ = "trains"

    train_number: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
    train_name: Mapped[str] = mapped_column(String(100), nullable=False)
    train_type: Mapped[str] = mapped_column(String(50), nullable=False)
    origin_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    destination_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    service_pattern: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_synthetic_schedule: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)



class TrainSchedule(Base):
    __tablename__ = "train_schedules"

    schedule_id: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
    train_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    station_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    station_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    arrival_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    departure_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    day: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    km_from_origin: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

class TrainMovement(Base):
    __tablename__ = "train_movements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    train_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    delay_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    direction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), default="SCHEDULED", nullable=True)


