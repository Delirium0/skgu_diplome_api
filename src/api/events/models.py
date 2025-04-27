from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.database.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_background = Column(String, nullable=False)
    event_creator_name = Column(String, nullable=False)
    event_creator_image = Column(String, nullable=True)
    event_rating = Column(Float, nullable=True)
    event_time = Column(DateTime(timezone=True), nullable=False)
    event_name = Column(String, nullable=False)
    event_description = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key к таблице users

    is_moderate = Column(Boolean, default=False)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    creator = relationship("User", backref="created_events")  # Связь с моделью User
    address = Column(String, nullable=True)
