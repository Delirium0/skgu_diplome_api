from typing import List, Optional

from sqlalchemy import select, or_, func
from sqlalchemy.orm import joinedload, selectinload

from config import DATABASE_URL
from src.api.search.database.models import Floor, Node, Edge, Location
from src.database.singleton_database import DatabaseSingleton
from src.api.locations.schemas import LocationsInfo, LocationCreate


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


loc_repo = LocationsRepository()
