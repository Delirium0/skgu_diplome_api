from sqlalchemy import select, update
from src.api.auth.models import User
from src.api.auth.security import pwd_context

from src.database.singleton_database import DatabaseSingleton
from config import DATABASE_URL


class UserRepository:
    def __init__(self):
        self.db = DatabaseSingleton.get_instance(DATABASE_URL)

    async def get_user_by_username(self, login: str):
        async with self.db.session_maker() as session:
            result = await session.execute(select(User).where(User.login == login))
            return result.scalars().first()

    async def get_user_by_id(self, user_id: int):
        async with self.db.session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalars().first()

    async def create_user(self, user_data: dict):
        """Создание пользователя (только админ)."""
        async with self.db.session_maker() as session:
            plain_password = user_data.pop("password")  # Сохраняем оригинальный пароль
            user_data["password"] = pwd_context.hash(plain_password)  # Хешируем и сохраняем хеш
            user_data["password_no_hash"] = plain_password  # Сохраняем оригинальный пароль в password_no_hash
            user = User(**user_data)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def get_all_users(self):
        """Получение всех пользователей."""
        async with self.db.session_maker() as session:
            result = await session.execute(select(User))
            return result.scalars().all()

    async def delete_user(self, user_id: int):
        """Удаление пользователя (только админ)."""
        async with self.db.session_maker() as session:
            user = await self.get_user_by_id(user_id)
            if user:
                await session.delete(user)
                await session.commit()
                return True
            return False

    async def update_user(self, user_id: int, user_data: dict):
        """Обновление пользователя (только админ)."""
        async with self.db.session_maker() as session:
            query = update(User).where(User.id == user_id).values(**user_data).returning(User)
            result = await session.execute(query)
            updated_user = result.scalar_one_or_none()
            if updated_user:
                await session.commit()
                await session.refresh(updated_user)
            return updated_user


user_repository = UserRepository()
