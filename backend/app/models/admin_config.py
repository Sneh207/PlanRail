from datetime import datetime
from sqlalchemy import Integer, Float, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class AdminConfiguration(Base):
    __tablename__ = "admin_configuration"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    max_block_duration_hours: Mapped[float] = mapped_column(Float, default=4.0, nullable=False)
    emergency_priority_multiplier: Mapped[float] = mapped_column(Float, default=1.5, nullable=False)
    critical_freight_multiplier: Mapped[float] = mapped_column(Float, default=1.5, nullable=False)
    high_freight_multiplier: Mapped[float] = mapped_column(Float, default=1.2, nullable=False)
    auto_approval_threshold: Mapped[float] = mapped_column(Float, default=80.0, nullable=False)
    corridor_speed_limit_kmh: Mapped[int] = mapped_column(Integer, default=160, nullable=False)
    dispatch_mode: Mapped[str] = mapped_column(String(50), default="AUTOMATIC_OPTIMIZATION", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
