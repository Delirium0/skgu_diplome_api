import time
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.openapi.models import Response
from starlette import status

from src.api.auth.service import user_is_admin
from src.api.locations.locations_repo import loc_repo
from src.api.locations.schemas import LocationsInfo, LocationInfo, LocationCreate, LocationInfoDetail, \
    FloorInfo, LocationsInfoMP, LocationWithBoundsResponse, LocationUpdate  # Import FloorInfo
from src.api.search.database.models import Location

router = APIRouter(prefix='/locations', tags=["Locations"])


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


# GET /admin/locations - Список локаций для админки
@router.get("/admin/locations", response_model=List[LocationInfo], dependencies=[Depends(user_is_admin)])
async def get_all_locations_for_admin():
    """Получение списка всех локаций (для админки)."""
    locations = await loc_repo.get_all_locations_admin()
    # Преобразуем в Pydantic модель, если репозиторий вернул полные объекты
    return [LocationInfo.model_validate(loc) for loc in locations]


# GET /admin/locations/{location_id} - Получение локации с bounds для редактирования
@router.get("/admin/locations/{location_id}", response_model=LocationWithBoundsResponse,
            dependencies=[Depends(user_is_admin)])
async def get_location_with_bounds_for_admin(location_id: int):
    """Получение локации с границами по ID (для админки)."""
    location = await loc_repo.get_location_with_bounds_by_id(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    bounds_data = [[bound.lat, bound.lng] for bound in location.bounds]
    # Собираем ответ
    location_response = LocationWithBoundsResponse(
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
        building_type_name_ru=location.building_type_name_ru,
        bounds=bounds_data
    )
    return location_response


# PUT /admin/locations/{location_id} - Обновление локации
@router.put("/admin/locations/{location_id}", response_model=LocationWithBoundsResponse,
            dependencies=[Depends(user_is_admin)])
async def update_location_admin(
        location_id: int,
        location_data: LocationUpdate,
):
    """Обновление локации, включая границы (для админки)."""
    # Если bounds в теле LocationUpdate, извлекаем их:
    # new_bounds_data = location_data.bounds
    # del location_data.bounds # Удаляем из основных данных перед передачей в репо
    # Если bounds передаются отдельным параметром:
    new_bounds_data = location_data.bounds
    update_data_for_repo = location_data.model_dump(exclude_unset=True, exclude={'bounds'})

    updated_location = await loc_repo.update_location(
        location_id,
        update_data_for_repo,  # Словарь с основными полями для обновления
        new_bounds_data  # Отдельный список bounds
    )
    if not updated_location:
        raise HTTPException(status_code=404, detail="Location not found")

    updated_bounds_data = [[bound.lat, bound.lng] for bound in updated_location.bounds]
    location_response = LocationWithBoundsResponse(
        id=updated_location.id,
        lat=updated_location.lat,
        lng=updated_location.lng,
        title=updated_location.title,
        type=updated_location.type,
        address=updated_location.address,
        time_start=updated_location.time_start,
        time_end=updated_location.time_end,
        main_icon=updated_location.main_icon,
        building_type=updated_location.building_type,
        building_type_name_ru=updated_location.building_type_name_ru,
        bounds=updated_bounds_data
    )
    return location_response


# DELETE /admin/locations/{location_id} - Удаление локации
@router.delete("/admin/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(user_is_admin)])
async def delete_location_admin(location_id: int):
    """Удаление локации по ID (для админки)."""
    deleted = await loc_repo.delete_location(location_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Location not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/locations_main_page', response_model=List[LocationWithBoundsResponse])
async def get_all_locations():
    locations: List[Location] = await loc_repo.get_all_buildings_info_main()

    locations_response = []
    for location in locations:
        bounds_data = [[bound.lat, bound.lng] for bound in location.bounds]

        # Создаем объект ответа Pydantic
        location_data = LocationWithBoundsResponse(
            id=location.id,
            lat=location.lat,
            lng=location.lng,
            title=location.title,
            type=location.type,  # Убедитесь, что поле 'type' есть в модели Location
            address=location.address,
            time_start=location.time_start,
            time_end=location.time_end,
            main_icon=location.main_icon,
            building_type=location.building_type,
            building_type_name_ru=location.building_type_name_ru,
            bounds=bounds_data
        )
        locations_response.append(location_data)

    return locations_response


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


@router.get('/locations/{location_id}', response_model=LocationInfoDetail)
async def get_location_by_id_endpoint(location_id: int):
    """Gets a specific location by ID, including floors."""
    location = await loc_repo.get_location_by_id(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    floor_info_list = []
    if location.floors:
        floor_info_list = [FloorInfo.model_validate(floor) for floor in location.floors]
    location_info = LocationInfoDetail(
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
        building_type_name_ru=location.building_type_name_ru,
        floors=floor_info_list
    )
    return location_info
