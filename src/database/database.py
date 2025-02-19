from abc import ABC, abstractmethod
from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = MetaData()


# базовое подключение к бд
class DatabaseInterface(ABC):
    @abstractmethod
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        pass
