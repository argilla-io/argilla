from enum import Enum


class PredictionStatus(str, Enum):
    OK = "ok"
    KO = "ko"

    def __str__(self) -> str:
        return str(self.value)
