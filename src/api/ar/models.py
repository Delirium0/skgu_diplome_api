from typing import List, Optional

from sqlalchemy import String, Integer, Identity, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.database import Base
from src.api.search.database.models import Floor

class Room(Base):
    """
    Модель кабинета для AR.
    """
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    room_number: Mapped[str] = mapped_column(String, nullable=False, comment="Номер кабинета")
    room_name: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="Название кабинета")
    target_index: Mapped[int] = mapped_column(Integer, nullable=False, comment="Индекс цели в AR (0, 1, 2...)")
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="Описание кабинета")

    floor_id: Mapped[int] = mapped_column(Integer, ForeignKey("floors.id", ondelete="CASCADE"), nullable=False)
    floor: Mapped["Floor"] = relationship(back_populates="rooms")
