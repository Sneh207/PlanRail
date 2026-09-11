from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class MaintenanceHistory(Base):
    __tablename__ = "maintenance_history"

    history_id: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
    asset_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    event_date: Mapped[str] = mapped_column(String(50), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[float] = mapped_column(Float, nullable=False)
    downtime_hours: Mapped[float] = mapped_column(Float, nullable=False)

