from enum import Enum

from rubrix.server.apis.v0.models.commons.model import TaskType as _TaskType


class TaskType(str, Enum):
    text_classification = "text_classification"
    token_classification = "token_classification"
    text2text = "text2text"

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def as_old_task_type(self) -> _TaskType:
        """
        Converts task type to old task type enum

        Returns:
            The old task type enum version from defined
        """
        value = _TASK_TYPES_MAP_.get(self)
        if not value:
            raise RuntimeError(f"Unmapped value '{self}'")
        return value

    @classmethod
    def from_old_task_type(cls, value: _TaskType) -> "TaskType":
        """
        Build task type from old task definition

        Args:
            value: The old task type definition

        Returns:
            The task type

        """
        return TaskType(value.name)


_TASK_TYPES_MAP_ = {
    TaskType.text_classification: _TaskType.text_classification,
    TaskType.token_classification: _TaskType.token_classification,
    TaskType.text2text: _TaskType.text2text,
}
