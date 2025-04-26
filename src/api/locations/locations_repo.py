from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from config import DATABASE_URL
from src.api.locations.schemas import LocationCreate
from src.api.locations.schemas import LocationUpdate
from src.api.search.database.models import Location, Bounds
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

    async def get_all_locations_admin(self) -> list[Location]:  # Новый метод для админ-списка
        """Получает список всех локаций для админки."""
        async with self.db.session_maker() as session:
            # Можно выбрать нужные поля или вернуть полные объекты Location
            result = await session.execute(
                select(Location).order_by(Location.id)
                # Если нужны bounds в списке, добавить .options(selectinload(Location.bounds))
            )
            return result.scalars().all()

    async def get_all_buildings_info(self) -> list[Location]:
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Location.id, Location.building_type, Location.building_type_name_ru, Location.time_end,
                       Location.time_start, Location.address, Location.title, Location.main_icon)
            )
            return result.all()

    async def get_all_buildings_info_main(self) -> list[Location]:
        async with self.db.session_maker() as session:
            stmt = select(Location).options(selectinload(Location.bounds))
            result = await session.execute(stmt)
            locations = result.scalars().all()
            return list(locations)

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

    async def get_location_with_bounds_by_id(self, location_id: int) -> Optional[Location]:
        """Gets a specific location by ID, including its bounds."""
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Location)
                .where(Location.id == location_id)
                .options(selectinload(Location.bounds))  # Загружаем связанные границы
                # Если нужны и этажи в админке, добавить .options(selectinload(Location.floors))
            )
            return result.scalar_one_or_none()

    async def update_location(self, location_id: int,
                              # Явно укажем, что ожидаем словарь, а не Pydantic модель
                              location_data_dict: dict,
                              new_bounds_data: Optional[List[List[float]]]) -> Optional[Location]:
        """Updates an existing location, including its bounds."""
        async with self.db.session_maker() as session:
            # Загружаем сразу с bounds, если они нужны для каких-то проверок до обновления
            location = await session.get(Location, location_id,
                                         options=[selectinload(Location.bounds)])
            if not location:
                return None

            # --- ИЗМЕНЕНО: Работаем напрямую со словарем ---
            # Словарь location_data_dict уже содержит только те поля,
            # которые нужно обновить (благодаря exclude_unset=True в роутере).
            for key, value in location_data_dict.items():
                # Проверяем, есть ли такой атрибут у модели Location, чтобы избежать ошибок
                if hasattr(location, key):
                    setattr(location, key, value)
                else:
                    # Логирование или предупреждение, если пришло неожиданное поле
                    print(f"Предупреждение: Попытка обновить несуществующее поле '{key}' в Location.")

            # Обновление bounds: удаляем старые, добавляем новые
            if new_bounds_data is not None:
                # Используем существующую логику обновления bounds
                # Убедитесь, что relationship в модели Location настроен с cascade="all, delete-orphan"
                # чтобы SQLAlchemy сам удалил старые Bounds при присвоении нового списка.
                location.bounds = [Bounds(lat=b[0], lng=b[1]) for b in new_bounds_data]
            # Если new_bounds_data равен None, то границы не трогаем

            await session.commit()
            # Обновляем объект из БД, чтобы получить актуальные данные, включая ID новых bounds
            await session.refresh(location, attribute_names=['bounds'])  # Явно обновляем bounds
            return location

    async def delete_location(self, location_id: int) -> bool:
        """Deletes a location by ID."""
        async with self.db.session_maker() as session:
            location = await session.get(Location, location_id)
            if location:
                await session.delete(location)
                await session.commit()
                return True
            return False


loc_repo = LocationsRepository()
