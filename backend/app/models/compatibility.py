from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class MaintenanceCompatibility(Base):
    __tablename__ = "maintenance_compatibility"
    __table_args__ = (
        UniqueConstraint("department_a", "department_b", name="uq_department_pair"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    department_a: Mapped[str] = mapped_column(String(50), nullable=False)
    department_b: Mapped[str] = mapped_column(String(50), nullable=False)
    compatibility: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
