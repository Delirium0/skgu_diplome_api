import asyncio
import base64
from typing import AsyncGenerator
from typing import List, Dict, Optional

from sqlalchemy import Identity, UniqueConstraint
from sqlalchemy import MetaData, NullPool
from sqlalchemy import String, Float, ForeignKey, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.database import Base


class Floor(Base):
    """
    Модель этажа.
    """
    __tablename__ = "floors"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    building_number: Mapped[str] = mapped_column(String, nullable=False)
    floor_number: Mapped[int] = mapped_column(Integer, nullable=False, comment="Номер этажа")
    image_data: Mapped[str] = mapped_column(String, nullable=False, comment="Изображение этажа в формате Base64")

    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("locations.id", ondelete="SET NULL"),
                                                    nullable=True)

    nodes: Mapped[List["Node"]] = relationship(back_populates="floor")
    edges: Mapped[List["Edge"]] = relationship(back_populates="floor")
    location: Mapped["Location"] = relationship("Location", back_populates="floors")


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


class Location(Base):
    """
    Модель локации (наружные точки, здания).
    """
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    time_start: Mapped[str] = mapped_column(nullable=True)
    time_end: Mapped[str] = mapped_column(nullable=True)
    main_icon: Mapped[str | None] = mapped_column(nullable=True)

    building_type: Mapped[str] = mapped_column(String, nullable=True)
    building_type_name_ru: Mapped[str] = mapped_column(String, nullable=True)

    bounds: Mapped[list["Bounds"]] = relationship("Bounds", back_populates="location", cascade="all, delete-orphan")
    floors: Mapped[List["Floor"]] = relationship("Floor", back_populates="location", cascade="all, delete-orphan")


class Bounds(Base):
    __tablename__ = "bounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id", ondelete="CASCADE"))
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)

    location: Mapped["Location"] = relationship("Location", back_populates="bounds")


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


from sqlalchemy import delete, select


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
                    weight=edge_data[2] if len(edge_data) > 2 else None,
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

    import json
    # # корпус 5 этаж 1
    # with open(r"E:\PycharmProjects\skgu_diplome_api\src\api\search\new\new_floor1_building_5.json", 'r',
    #           encoding='utf-8') as f:
    #     data = json.load(f)
    #
    # await load_data_to_db(db, data, building_number="5", floor_number=1)
    #
    # # корпус 6 этаж 1
    # with open(r"E:\PycharmProjects\skgu_diplome_api\src\api\search\new\new_floor1_building1.json", 'r',
    #           encoding='utf-8') as f:
    #     data = json.load(f)
    #
    # await load_data_to_db(db, data, building_number="6", floor_number=1)
    # # корпус 6 этаж 2
    # with open(r"E:\PycharmProjects\skgu_diplome_api\src\api\search\new\new_floor2_building1.json", 'r',
    #           encoding='utf-8') as f:
    #     data = json.load(f)
    #
    # await load_data_to_db(db, data, building_number="6", floor_number=2)

    # корпус 6 этаж 3
    with open(r"E:\PycharmProjects\skgu_diplome_api\src\search\buiding_6_floor_4.json", 'r',
              encoding='utf-8') as f:
        data = json.load(f)

    await load_data_to_db(db, data, building_number="6", floor_number=4)


async def delete_floor_data(db: SQLAlchemyDatabase, building_number: str, floor_number: int):
    """
    Удаляет данные этажа из базы данных по номеру здания и этажа.
    """
    async for session in db.get_session():
        try:
            # 1. Находим этаж, который нужно удалить
            query = select(Floor).where(Floor.building_number == building_number, Floor.floor_number == floor_number)
            result = await session.execute(query)
            floor_to_delete = result.scalar_one_or_none()

            if floor_to_delete:
                floor_id_to_delete = floor_to_delete.id

                # 2. Удаляем связанные Node и Edge (важно сделать это ПЕРЕД удалением Floor)
                delete_nodes_query = delete(Node).where(Node.floor_id == floor_id_to_delete)
                await session.execute(delete_nodes_query)

                delete_edges_query = delete(Edge).where(Edge.floor_id == floor_id_to_delete)
                await session.execute(delete_edges_query)

                # 3. Удаляем сам этаж
                delete_floor_query = delete(Floor).where(Floor.id == floor_id_to_delete)
                await session.execute(delete_floor_query)

                await session.commit()
                print(f"Данные для здания '{building_number}', этажа '{floor_number}' успешно удалены.")
            else:
                print(f"Этаж с зданием '{building_number}' и этажом '{floor_number}' не найден.")

        except Exception as e:
            await session.rollback()  # Откатываем транзакцию в случае ошибки
            print(f"Ошибка при удалении данных: {e}")
            raise


async def main_delete():
    from config import DATABASE_URL  # Убедитесь, что у вас есть config.py с DATABASE_URL
    db = DatabaseSingleton.get_instance(DATABASE_URL)

    # Укажите номер здания и этаж, которые нужно удалить
    building_number_to_delete = "6"  # Замените на номер вашего тестового здания
    floor_number_to_delete = 4  # Замените на номер вашего тестового этажа

    await delete_floor_data(db, building_number_to_delete, floor_number_to_delete)


if __name__ == '__main__':
    asyncio.run(main_delete())
