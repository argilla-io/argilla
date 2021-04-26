from enum import Enum


class TaskType(str, Enum):
    TEXTCLASSIFICATION = "TextClassification"
    TOKENCLASSIFICATION = "TokenClassification"
    TEXTTOTEXT = "TextToText"
    MULTITASKTEXTTOKENCLASSIFICATION = "MultitaskTextTokenClassification"

    def __str__(self) -> str:
        return str(self.value)
