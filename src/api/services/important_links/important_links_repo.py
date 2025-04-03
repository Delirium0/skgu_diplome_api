from sqlalchemy import select

from config import DATABASE_URL
from src.api.services.important_links.models import ImportantLinks  # Убедитесь, что путь к модели верный
from src.database.singleton_database import DatabaseSingleton


class ImportantLinksRepository:
    def __init__(self):
        self.db = DatabaseSingleton.get_instance(DATABASE_URL)

    async def add_link(self, link: str, link_text: str, icon: str | None) -> int:
        """
        Добавляет новую важную ссылку в базу данных.
        """
        async with self.db.session_maker() as session:
            important_link = ImportantLinks(
                link=link,
                link_text=link_text,
                icon=icon
            )
            session.add(important_link)
            await session.commit()
            return important_link.id

    async def get_link_by_id(self, link_id: int) -> ImportantLinks | None:
        """
        Получает важную ссылку по ID.
        """
        async with self.db.session_maker() as session:
            # Используем session.execute(select(...)) и получаем скалярный результат
            result = await session.execute(select(ImportantLinks).where(ImportantLinks.id == link_id))
            return result.scalar_one_or_none() # Используем scalar_one_or_none, чтобы получить один ORM объект или None

    async def get_all_links(self) -> list[ImportantLinks]:
        """
        Получает все важные ссылки.
        """
        async with self.db.session_maker() as session:
            # Используем session.execute(select(...)) и получаем список скалярных результатов
            result = await session.execute(select(ImportantLinks))
            return result.scalars().all() # Используем scalars().all(), чтобы получить список ORM объектов

    async def update_link(self, link_id: int, link: str | None, link_text: str | None,
                          icon: str | None) -> ImportantLinks | None:
        """
        Обновляет существующую важную ссылку.
        """
        async with self.db.session_maker() as session:
            important_link = await session.get(ImportantLinks, link_id)
            if important_link:
                if link is not None:
                    important_link.link = link
                if link_text is not None:
                    important_link.link_text = link_text
                if icon is not None:
                    important_link.icon = icon
                await session.commit()
                return important_link
            return None

    async def delete_link(self, link_id: int) -> bool:
        """
        Удаляет важную ссылку по ID.
        """
        async with self.db.session_maker() as session:
            important_link_result = await session.execute(select(ImportantLinks).where(ImportantLinks.id == link_id))
            important_link = important_link_result.scalar_one_or_none()
            if important_link:
                await session.delete(important_link)
                await session.commit()
                return True
            return False


repo_links = ImportantLinksRepository()


# Пример использования:
async def main():
    # Пример добавления ссылки
    new_link_id = await repo_links.add_link(
        link="https://example.com",
        link_text="Пример ссылки",
        icon='<svg>...</svg>'  # или None, если нет иконки
    )
    print(f"Добавлена ссылка с ID: {new_link_id}")

    # Пример получения ссылки по ID
    link = await repo_links.get_link_by_id(new_link_id)
    if link:
        print(f"Получена ссылка: {link.link_text}, URL: {link.link}")
    else:
        print("Ссылка не найдена")

    # Пример получения всех ссылок
    all_links = await repo_links.get_all_links()
    print("Все ссылки:")
    for l in all_links:
        print(f"ID: {l.id}, Текст: {l.link_text}, URL: {l.link}")

    # Пример обновления ссылки
    updated_link = await repo_links.update_link(new_link_id, link_text="Обновленный текст ссылки")
    if updated_link:
        print(f"Ссылка обновлена, новый текст: {updated_link.link_text}")

    # Пример удаления ссылки
    deleted = await repo_links.delete_link(new_link_id)
    if deleted:
        print(f"Ссылка с ID {new_link_id} удалена")
    else:
        print(f"Не удалось удалить ссылку с ID {new_link_id}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
