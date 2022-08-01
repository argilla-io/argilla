from enum import Enum


class TaskStatus(str, Enum):
    default = "Default"
    edited = "Edited"  # TODO: DEPRECATE
    discarded = "Discarded"
    validated = "Validated"


class TaskType(str, Enum):

    text_classification = "TextClassification"
    token_classification = "TokenClassification"
    text2text = "Text2Text"
    multi_task_text_token_classification = "MultitaskTextTokenClassification"


class PredictionStatus(str, Enum):
    OK = "ok"
    KO = "ko"
