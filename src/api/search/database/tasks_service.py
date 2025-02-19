import uuid
from datetime import datetime

from src.telegram_bot.database.models import UserTaskCompletion
from src.telegram_bot.database.tasks.tasks_repository import TasksRepository
from src.telegram_bot.database.user.user_service import user_service


class TasksService:
    def __init__(self, tasks: TasksRepository):
        self.tasks = tasks

    async def post_tasks_test(self, channel_link: str, channel_id: int, num_users_capable_perform: int, reward: float):
        return await self.tasks.post_tasks_test(channel_link, channel_id, num_users_capable_perform, reward)

    async def post_task(self, channel_link: str, channel_id: int, num_users_capable_perform: int, reward: float):
        return await self.tasks.post_task(channel_link, channel_id, num_users_capable_perform, reward)

    async def get_available_tasks(self, user_id: int):
        return await self.tasks.get_available_tasks(user_id)

    async def get_task_by_id(self, task_id: int):
        return await self.tasks.get_task_by_id(task_id)

    async def delete_task(self, task_id: int):
        await self.tasks.delete_task(task_id)

    async def get_task_by_channel_id(self, channel_id: uuid):
        return await self.tasks.get_task_by_channel_id(channel_id)

    async def task_complete(self, task_id: uuid, user_id: int):
        return await self.tasks.task_complete(task_id, user_id)

    async def task_decrease_execution(self, task_id: uuid, current_execution: int):
        return await self.tasks.task_decrease_execution(task_id, current_execution)

    async def get_all_tasks(self):
        return await self.tasks.get_all_tasks()

    async def task_completed_process(self, user_id: int, task_id: int):  # Изменено: task_id вместо channel_id
        task = await self.get_task_by_id(task_id=task_id)  # Изменено: get_task_by_id
        user = await user_service.get_user_by_id(user_id)
        # print(channel_id, task, "задача есть вот айди канала задачи")
        if task:
            task_complete = await self.tasks.user_completed_task(task.id, user_id)
            # print(task_complete)
            if task_complete:
                return True
            else:
                num_users_capable_perform = task.num_users_capable_perform
                if num_users_capable_perform > 0:
                    # print('задача выполнена и есть еще разрешение выполнять')
                    await self.task_complete(task.id, user_id)
                    await self.task_decrease_execution(task.id, num_users_capable_perform)
                    await user_service.add_points_completed_tasks(user_id, task.reward, user)
                    return True


repo_tasks = TasksRepository()

tasks_service = TasksService(repo_tasks)
