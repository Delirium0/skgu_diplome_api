from typing import Optional, List

from pydantic import BaseModel


class FloorInfo(BaseModel):
    id: int
    building_number: str
    floor_number: int
    image_data: str  # Base64 image data

    class Config:
        from_attributes = True


class LocationsInfo(BaseModel):
    id: int
    building_type: Optional[str] = None
    building_type_name_ru: Optional[str] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    address: str
    title: str
    main_icon: Optional[str] = None


class LocationsInfoMP(BaseModel):
    id: int
    building_type: Optional[str] = None
    building_type_name_ru: Optional[str] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    address: str
    title: str
    main_icon: Optional[str] = None


class LocationWithBoundsResponse(BaseModel):
    id: int
    lat: float  # Добавлено, так как есть в примере вывода
    lng: float  # Добавлено, так как есть в примере вывода
    title: str
    type: str  # Добавлено, так как есть в примере вывода
    address: str
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    main_icon: Optional[str] = None
    building_type: Optional[str] = None  # Добавлено, так как есть в примере вывода (хотя там нет)
    building_type_name_ru: Optional[str] = None  # Добавлено, так как есть в примере вывода (хотя там нет)
    bounds: List[List[float]]  # Список списков [lat, lng]


class LocationInfo(BaseModel):
    id: int
    lat: float
    lng: float
    title: str
    type: str
    address: str
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    main_icon: Optional[str] = None
    building_type: Optional[str] = None
    building_type_name_ru: Optional[str] = None


class LocationCreate(BaseModel):
    lat: float
    lng: float
    title: str
    type: str
    address: str
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    main_icon: Optional[str] = None
    building_type: Optional[str] = None
    building_type_name_ru: Optional[str] = None


class LocationInfoDetail(LocationInfo):
    floors: Optional[List[FloorInfo]] = None  # Добавляем список этажей
