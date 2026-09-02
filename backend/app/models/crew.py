from datetime import datetime
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class CrewAvailability(Base):
    __tablename__ = "crew_availability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crew_id: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    crew_name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    available_from_hour: Mapped[int] = mapped_column(Integer, nullable=False)
    available_to_hour: Mapped[int] = mapped_column(Integer, nullable=False)
    team_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
