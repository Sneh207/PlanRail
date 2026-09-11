from typing import Optional
from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    request_id: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
    asset_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    maintenance_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[float] = mapped_column(Float, nullable=False)
    criticality_score: Mapped[float] = mapped_column(Float, nullable=False)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    created_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    due_date: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    overdue_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    baseline_risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True, nullable=False)


