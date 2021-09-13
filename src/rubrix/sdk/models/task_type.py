from enum import Enum


class TaskType(str, Enum):
    TEXTCLASSIFICATION = "TextClassification"
    TOKENCLASSIFICATION = "TokenClassification"
    TEXT2TEXT = "Text2Text"
    MULTITASKTEXTTOKENCLASSIFICATION = "MultitaskTextTokenClassification"

    def __str__(self) -> str:
        return str(self.value)
