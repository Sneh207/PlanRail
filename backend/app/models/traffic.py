from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class TrafficWindow(Base):
    __tablename__ = "traffic_windows"

    traffic_window_id: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
    section_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    train_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    traffic_level: Mapped[str] = mapped_column(String(50), nullable=False)
