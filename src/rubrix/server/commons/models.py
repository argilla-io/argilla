from enum import Enum


class TaskStatus(str, Enum):
    default = "Default"
    edited = "Edited"  # TODO: DEPRECATE
    discarded = "Discarded"
    validated = "Validated"
