from sqlalchemy import MetaData, NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator

from src.database.database import DatabaseInterface


# подключение именно для алхимии
class SQLAlchemyDatabase(DatabaseInterface):
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.base = declarative_base()
        self.metadata = MetaData()
        self.engine = create_async_engine(self.db_url, poolclass=NullPool)
        self.session_maker = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_maker() as session:
            try:
                yield session
            finally:
                await session.close()
