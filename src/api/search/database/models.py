import base64
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Identity, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

Base = declarative_base()


class Floor(Base):
    """
    Модель этажа.
    """
    __tablename__ = "floors"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    building_number: Mapped[str] = mapped_column(String, nullable=False)
    floor_number: Mapped[int] = mapped_column(Integer, nullable=False, comment="Номер этажа")
    image_data: Mapped[str] = mapped_column(String, nullable=False, comment="Изображение этажа в формате Base64")
    nodes: Mapped[List["Node"]] = relationship(back_populates="floor")
    edges: Mapped[List["Edge"]] = relationship(back_populates="floor")


class Node(Base):
    """
    Модель узла на этаже.
    """
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    floor_id: Mapped[int] = mapped_column(Integer, ForeignKey("floors.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, comment="Уникальное имя узла на этаже")
    x: Mapped[float] = mapped_column(Float, nullable=False, comment="Координата X узла")
    y: Mapped[float] = mapped_column(Float, nullable=False, comment="Координата Y узла")
    type: Mapped[str] = mapped_column(String, nullable=False, comment="Тип узла (office, corridor, etc.)")
    name_ru: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="Имя узла на русском")
    name_en: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="Имя узла на английском")
    name_kz: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="Имя узла на казахском")
    description_ru: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="Описание узла на русском")
    description_en: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="Описание узла на английском")
    description_kz: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="Описание узла на казахском")

    floor: Mapped["Floor"] = relationship(back_populates="nodes")

    __table_args__ = (UniqueConstraint('floor_id', 'name', name='unique_node_name_per_floor'),)


class Edge(Base):
    """
    Модель ребра, соединяющего два узла на этаже.
    """
    __tablename__ = "edges"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    floor_id: Mapped[int] = mapped_column(Integer, ForeignKey("floors.id"), nullable=False)
    source_node_name: Mapped[str] = mapped_column(String, nullable=False, comment="Имя начального узла")
    target_node_name: Mapped[str] = mapped_column(String, nullable=False, comment="Имя конечного узла")
    weight: Mapped[Optional[Float]] = mapped_column(Float, nullable=True,
                                                    comment="Вес ребра (расстояние, время и т.п.)")

    floor: Mapped["Floor"] = relationship(back_populates="edges")
    __table_args__ = (
        UniqueConstraint('floor_id', 'source_node_name', 'target_node_name', name='unique_edge_per_floor'),)


from sqlalchemy import MetaData, NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator


# from src.database.database import DatabaseInterface # Убрал, потому что нет примера DatabaseInterface


# подключение именно для алхимии
class SQLAlchemyDatabase:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.base = Base  # Use the Base we already defined
        self.metadata = MetaData()
        self.engine = create_async_engine(self.db_url, poolclass=NullPool)
        self.session_maker = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_maker() as session:
            try:
                yield session
            finally:
                await session.close()


class DatabaseSingleton:
    _instance = None

    @staticmethod
    def get_instance(db_url: str):
        if DatabaseSingleton._instance is None:
            DatabaseSingleton._instance = SQLAlchemyDatabase(db_url)
        return DatabaseSingleton._instance


async def create_db_and_tables(db: SQLAlchemyDatabase):
    """
    Создает базу данных и таблицы, если они еще не существуют.
    """
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def image_to_base64(image_path: str) -> str:
    """
    Кодирует изображение в формат Base64.
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string


async def load_data_to_db(db: SQLAlchemyDatabase, data: Dict, building_number: str, floor_number: int):
    """
    Загружает данные из JSON в базу данных.
    """

    try:
        async for session in db.get_session():
            building_number = building_number
            image_path = data.get("image_path")

            # Кодируем изображение в Base64
            image_data = image_to_base64(image_path)

            # Создаем объект Floor
            floor = Floor(building_number=building_number, image_data=image_data, floor_number=floor_number)
            session.add(floor)
            await session.flush()  # Получаем ID этажа

            nodes_data = data.get("nodes", {})
            edges_data = data.get("edges", [])

            # Создаем объекты Node
            nodes = [
                Node(
                    floor_id=floor.id,
                    name=node_name,
                    x=node_data["coords"][0],
                    y=node_data["coords"][1],
                    type=node_data.get("type"),
                    name_ru=node_data.get("name").get('ru'),
                    name_en=node_data.get("name").get('en'),
                    name_kz=node_data.get("name").get('kz'),
                    description_ru=node_data.get("description").get('ru'),
                    description_en=node_data.get("description").get('en'),
                    description_kz=node_data.get("description").get('kz'),
                )
                for node_name, node_data in nodes_data.items()
            ]
            session.add_all(nodes)

            # Создаем объекты Edge
            edges = [
                Edge(
                    floor_id=floor.id,
                    source_node_name=edge_data[0],
                    target_node_name=edge_data[1],
                    weight=edge_data[2] if len(edge_data) > 2 else None,  # Вес ребра может отсутствовать
                )
                for edge_data in edges_data
            ]
            session.add_all(edges)

            await session.commit()
            print("Данные успешно загружены в базу данных.")
            break  # Exit the loop after successful commit

    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        raise
    finally:
        pass  # No need to session.close() as it's handled by the async generator


async def main():
    # Пример использования
    from config import DATABASE_URL
    db = DatabaseSingleton.get_instance(DATABASE_URL)

    await create_db_and_tables(db)

    # Загрузите ваш JSON файл
    import json
    # корпус 5 этаж 1
    with open(r"E:\PycharmProjects\skgu_diplome_api\src\api\search\new\new_floor1_building_5.json", 'r',
              encoding='utf-8') as f:
        data = json.load(f)

    await load_data_to_db(db, data, building_number="5", floor_number=1)

    # корпус 6 этаж 1
    with open(r"E:\PycharmProjects\skgu_diplome_api\src\api\search\new\new_floor1_building1.json", 'r',
              encoding='utf-8') as f:
        data = json.load(f)

    await load_data_to_db(db, data, building_number="6", floor_number=1)
    # корпус 6 этаж 2
    with open(r"E:\PycharmProjects\skgu_diplome_api\src\api\search\new\new_floor2_building1.json", 'r',
              encoding='utf-8') as f:
        data = json.load(f)

    await load_data_to_db(db, data, building_number="6", floor_number=2)


if __name__ == '__main__':
    asyncio.run(main())
