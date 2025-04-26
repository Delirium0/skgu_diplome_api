# src/api/feedbacks/schemas.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FeedbackBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Оценка приложения от 1 до 5")
    comment: Optional[str] = Field(None, description="Текстовый комментарий к отзыву")


class UserInfo(BaseModel):
    id: int
    login: str
    model_config = ConfigDict(from_attributes=True)


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Новая оценка (если меняется)")
    comment: Optional[str] = Field(None, description="Новый комментарий (если меняется)")


class FeedbackResponse(FeedbackBase):
    id: int
    created_at: datetime
    user: UserInfo

    model_config = ConfigDict(from_attributes=True)
