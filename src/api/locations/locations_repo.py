from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from config import DATABASE_URL
from src.api.locations.schemas import LocationCreate
from src.api.search.database.models import Location
from src.database.singleton_database import DatabaseSingleton


class LocationsRepository:
    def __init__(self):
        self.db = DatabaseSingleton.get_instance(DATABASE_URL)

    async def get_all_buildings(self) -> list[Location]:
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Location)
            )
            return result.scalars().all()

    async def get_all_buildings_info(self) -> list[Location]:
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Location.id, Location.building_type, Location.building_type_name_ru, Location.time_end,
                       Location.time_start, Location.address, Location.title, Location.main_icon)
            )
            return result.all()

    async def create_location(self, location_data: LocationCreate) -> Location:  # Correct return type
        """Creates a new location in the database."""
        async with self.db.session_maker() as session:
            location = Location(**location_data.model_dump())
            session.add(location)
            await session.commit()
            await session.refresh(location)
            return location

    async def get_location_by_id(self, location_id: int) -> Optional[Location]:
        """Gets a specific location by its ID, including related floors."""
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Location)
                .where(Location.id == location_id)
                .options(selectinload(Location.floors))  # Загружаем связанные этажи
            )
            return result.scalar_one_or_none()


loc_repo = LocationsRepository()
