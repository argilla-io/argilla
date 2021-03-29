from enum import Enum


class TaskType(str, Enum):
    TEXTCLASSIFICATION = "TextClassification"
    TOKENCLASSIFICATION = "TokenClassification"

    def __str__(self) -> str:
        return str(self.value)
