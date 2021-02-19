from enum import Enum


class RecordStatus(str, Enum):
    DEFAULT = "Default"
    EDITED = "Edited"
    DISCARDED = "Discarded"
    VALIDATED = "Validated"

    def __str__(self) -> str:
        return str(self.value)
