from sqlalchemy import Identity
from sqlalchemy import String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class ImportantLinks(Base):
    """
    Модель этажа.
    """
    __tablename__ = "important_links"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    link: Mapped[str] = mapped_column(String, nullable=False)
    link_text: Mapped[str] = mapped_column(String, nullable=False)
    icon: Mapped[str | None] = mapped_column(nullable=True)
