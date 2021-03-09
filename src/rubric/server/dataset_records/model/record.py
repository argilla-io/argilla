from typing import Any, Dict, List, Optional

from pydantic import PrivateAttr, root_validator, validator
from rubric.logging import LoggingMixin
from rubric.server.commons.helpers import flatten_dict
from rubric.server.commons.models import BaseRecord, RecordTaskInfo, TaskType


class MultiTaskRecord(BaseRecord, LoggingMixin):
    """
    A general common dataset record model

    All task records will be part of a general dataset record
    """

    text: Dict[str, Any] = None

    tokens: List[str] = None
    raw_text: str = None

    __tasks__: Dict[TaskType, RecordTaskInfo] = PrivateAttr(default_factory=dict)

    @property
    def relevant_text(self) -> str:
        """The main record textual content"""

        if self.raw_text:
            return self.raw_text
        if self.text:
            return "\n".join(self.text.values())
        return ""

    @property
    def tasks(self) -> List[TaskType]:
        """Record task_meta.py"""
        return list(self.__tasks__.keys())

    def task_info(self, task: TaskType) -> Optional[RecordTaskInfo]:
        """
        Get the task info for task

        Parameters
        ----------
        task:
            The task type

        Returns
        -------
            Task info if exists. None otherwise

        """
        return self.__tasks__.get(task)

    def with_task_info(self, info: RecordTaskInfo):
        """
        Set task info for task

        Parameters
        ----------
        info:
            The task info

        """
        if info is None:
            raise ValueError("Missing task information")

        if info.task in self.__tasks__:
            self.logger.warning(
                "Task info already defined for task {}. It will be overrides",
                info.task,
            )

        self.__tasks__[info.task()] = info

        return self

    @validator("text")
    def flatten_text(cls, text: Dict[str, Any]):
        """Validator for flatten text data"""
        if text:
            return flatten_dict(text)
        return text

    @root_validator()
    def validate_record_inputs(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Checks record inputs"""
        text = values.get("text")
        tokens = values.get("tokens")

        assert text or tokens, "Must specify text or tokens input"
        return values
