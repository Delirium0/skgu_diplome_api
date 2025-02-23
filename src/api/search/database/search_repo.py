from typing import List, Optional

from sqlalchemy import select, or_, func
from sqlalchemy.orm import joinedload, selectinload

from config import DATABASE_URL
from src.api.search.database.models import Floor, Node, Edge, Location
from src.database.singleton_database import DatabaseSingleton


class MapRepository:
    def __init__(self):
        self.db = DatabaseSingleton.get_instance(DATABASE_URL)

    async def get_floor_by_building_and_floor_number(self, building_number: str, floor_number: int) -> Optional[Floor]:
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Floor).where(Floor.building_number == building_number, Floor.floor_number == floor_number)
            )
            return result.scalars().first()

    async def get_nodes_by_floor_id(self, floor_id: int) -> List[Node]:
        async with self.db.session_maker() as session:
            result = await session.execute(select(Node).where(Node.floor_id == floor_id))
            return result.scalars().all()

    async def get_edges_by_floor_id(self, floor_id: int) -> List[Edge]:
        async with self.db.session_maker() as session:
            result = await session.execute(select(Edge).where(Edge.floor_id == floor_id))
            return result.scalars().all()

    async def get_all_floors_by_building(self, building_number: str) -> List[Floor]:
        async with self.db.session_maker() as session:
            result = await session.execute(select(Floor).where(Floor.building_number == building_number))
            return result.scalars().all()

    async def get_location_by_building(self, building_number: str) -> Location:
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Location).join(Floor).where(Floor.building_number == building_number).options(
                    selectinload(Location.bounds))
            )
            return result.scalar()

    async def get_node_by_name_and_floor_id(self, node_name: str, floor_id: int) -> Optional[Node]:
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Node).where(Node.name == node_name, Node.floor_id == floor_id)
            )
            return result.scalars().first()

    async def search_nodes(self, term: str) -> List[Node]:
        async with self.db.session_maker() as session:
            result = await session.execute(
                select(Node)
                .options(joinedload(Node.floor))  # Eagerly load the 'floor' relationship
                .where(
                    or_(
                        func.lower(Node.name_ru).contains(term.lower()),
                        func.lower(Node.name_en).contains(term.lower()),
                        func.lower(Node.name_kz).contains(term.lower()),
                        func.lower(Node.description_ru).contains(term.lower()),
                        func.lower(Node.description_en).contains(term.lower()),
                        func.lower(Node.description_kz).contains(term.lower())
                    ),
                    Node.type != "corridor"  # Исключаем узлы с типом "corridor"
                ).limit(10)
            )
            return result.scalars().all()


map_repository = MapRepository()
