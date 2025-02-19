import uuid
from datetime import datetime

from sqlalchemy import select, desc
from sqlalchemy import update, delete

from config import DATABASE_URL
from src.database.singleton_database import DatabaseSingleton
from src.telegram_bot.database.models import TelegramUser, Referrals, DailyPoints, Tasks, UserTaskCompletion
from sqlalchemy import cast, Date
from src.telegram_bot.database.user.user_service import user_service


class TasksRepository:
    def __init__(self):
        self.db = DatabaseSingleton.get_instance(DATABASE_URL)

    async def post_tasks_test(self, channel_link: str, channel_id: int, num_users_capable_perform: int, reward: float):
        async with self.db.session_maker() as session:

            new_task = Tasks(channel_link=channel_link, channel_id=channel_id,
                             num_users_capable_perform=num_users_capable_perform,
                             reward=reward)
            session.add(new_task)
            await session.commit()

    async def post_task(self, channel_link: str, channel_id: int, num_users_capable_perform: int, reward: float):
        async with self.db.session_maker() as session:

            new_task = Tasks(channel_link=channel_link, channel_id=channel_id,
                             num_users_capable_perform=num_users_capable_perform,
                             reward=reward)
            session.add(new_task)
            await session.commit()

    async def get_available_tasks(self, user_id: int):
        async with self.db.session_maker() as session:

            # Получаем список всех заданий, которые еще можно выполнять
            completed_task_subquery = select(UserTaskCompletion.task_id).where(
                UserTaskCompletion.user_id == user_id
            ).subquery()

            # Изменение: явное использование select() для подзапроса
            requests = select(Tasks).where(
                Tasks.num_users_capable_perform != 0,
                ~Tasks.id.in_(select(completed_task_subquery.c.task_id))
            )

            tasks = (await session.execute(requests)).scalars().all()

            # Фильтруем задания, исключая уже выполненные
            available_tasks = [task for task in tasks if task.id not in tasks]

            return available_tasks

    async def get_all_tasks(self):
        async with self.db.session_maker() as session:

            all_tasks = await session.execute(select(Tasks))
            all_tasks = all_tasks.scalars().all()
            return all_tasks

    async def get_task_by_id(self, task_id: int):
        async with self.db.session_maker() as session:

            requests = select(Tasks).where(Tasks.id == task_id)
            result = await session.execute(requests)
            referrer = result.scalar()
            return referrer

    async def get_task_by_channel_id(self, channel_id: uuid):
        async with self.db.session_maker() as session:

            requests = select(Tasks).where(Tasks.channel_id == channel_id)
            result = await session.execute(requests)
            referrer = result.scalar()
            return referrer

    async def user_completed_task(self, task_id: uuid, user_id: int):
        # print(task_id, user_id, "задача и пользователь который выполнит ее ")
        async with self.db.session_maker() as session:


            user_task_completion = await session.execute(
                select(UserTaskCompletion).where(UserTaskCompletion.user_id == user_id,
                                                 UserTaskCompletion.task_id == task_id)
            )
            user_task_completion = user_task_completion.scalar()
            if user_task_completion:
                return True
            return False

    async def delete_task(self, task_id: int):
        async with self.db.session_maker() as session:

            await session.execute(delete(UserTaskCompletion).where(UserTaskCompletion.task_id == task_id))
            await session.execute(delete(Tasks).where(Tasks.id == task_id))
            await session.commit()

    async def task_complete(self, task_id: uuid, user_id: int):
        async with self.db.session_maker() as session:

            new_completion = UserTaskCompletion(user_id=user_id, task_id=task_id)
            session.add(new_completion)
            await session.commit()

    async def task_decrease_execution(self, task_id: uuid, current_execution: int):
        async with self.db.session_maker() as session:

            requests = update(Tasks).where(
                Tasks.id == task_id,
                Tasks.num_users_capable_perform > 0
            ).values(
                num_users_capable_perform=current_execution - 1
            ).returning(Tasks.num_users_capable_perform)

            result = await session.execute(requests)
            if result.scalar() is not None:
                await session.commit()
