from typing import List

from fastapi import APIRouter, Depends
from src.api.locations.locations_repo import loc_repo
from src.api.locations.schemas import LocationsInfo, LocationInfo, LocationCreate

router = APIRouter(prefix='/locations')


@router.get('/locations', response_model=List[LocationsInfo])
async def get_all_locations():
    locations = await loc_repo.get_all_buildings_info()
    locations_info = []
    for row in locations:
        location_info = LocationsInfo(
            id=row.id,
            building_type=row.building_type,
            building_type_name_ru=row.building_type_name_ru,
            time_start=row.time_start,
            time_end=row.time_end,
            address=row.address,
            title=row.title,
            main_icon=row.main_icon
        )
        locations_info.append(location_info)
    return locations_info


@router.post('/locations', response_model=LocationInfo)
async def create_location_endpoint(location_data: LocationCreate):
    """Creates a new location."""
    location = await loc_repo.create_location(location_data)
    location_info = LocationInfo(
        id=location.id,
        lat=location.lat,
        lng=location.lng,
        title=location.title,
        type=location.type,
        address=location.address,
        time_start=location.time_start,
        time_end=location.time_end,
        main_icon=location.main_icon,
        building_type=location.building_type,
        building_type_name_ru=location.building_type_name_ru
    )
    return location_info
