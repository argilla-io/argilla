from typing import Any, Optional, Type

from pydantic import BaseModel

from rubrix.server.tasks.commons import TaskType


class _TaskConfig(BaseModel):

    query: Any


class TaskFactory:

    _REGISTERED_TASKS = dict()

    @classmethod
    def register_task(
        cls,
        task_type: TaskType,
        query_request: Type[Any],
    ):
        cls._REGISTERED_TASKS[task_type] = _TaskConfig(query=query_request)

    @classmethod
    def get_task_by_task_type(cls, task_type: TaskType) -> Optional[_TaskConfig]:
        return cls._REGISTERED_TASKS.get(task_type)
