from typing import Optional
from datetime import date
from sqlalchemy import String, Float, Date, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class FreightTrainMovement(Base):
    __tablename__ = "freight_train_movements"

    freight_train_id: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
    movement_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    origin_station_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    destination_station_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    commodity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    load_tonnes: Mapped[float] = mapped_column(Float, nullable=False)
    planned_entry_time: Mapped[str] = mapped_column(String(20), nullable=False)
    planned_exit_time: Mapped[str] = mapped_column(String(20), nullable=False)
    traffic_priority: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    corridor: Mapped[str] = mapped_column(String(50), default="Delhi-Agra", nullable=False)
    data_status: Mapped[str] = mapped_column(String(50), default="SIMULATED_BY_PLANRAIL", nullable=False)
    source_basis: Mapped[str] = mapped_column(String(255), nullable=False)
    planning_use: Mapped[str] = mapped_column(String(255), nullable=False)
    simulation_note: Mapped[str] = mapped_column(Text, nullable=False)
    reference_1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reference_1_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reference_2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reference_2_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reference_3: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reference_3_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reference_4: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reference_4_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
