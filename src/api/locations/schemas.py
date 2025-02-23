from typing import Optional

from pydantic import BaseModel


class LocationsInfo(BaseModel):
    id: int
    building_type: str
    building_type_name_ru: Optional[str]
    time_start: str
    time_end: str
    address: str
    title: str
    main_icon: Optional[str]


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


class BoundsInfo(BaseModel):
    id: int
    location_id: int
    lat: float
    lng: float
