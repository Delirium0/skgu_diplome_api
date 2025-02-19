from fastapi import Query
from pydantic import BaseModel, Field


class RoutePoints(BaseModel):
    start: str = Field(default='1_entrance', description='Начальная точка от которой строится маршрут')
    target: str = Field(default='2_office_204', description='Точка до которой строится маршрут')
    building: str = Field(default="6", description='номер корпуса')