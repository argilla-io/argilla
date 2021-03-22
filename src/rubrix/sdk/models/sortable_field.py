from enum import Enum


class SortableField(str, Enum):
    PREDICTED_AS = "predicted_as"
    ANNOTATED_AS = "annotated_as"
    ANNOTATED_BY = "annotated_by"
    PREDICTED_BY = "predicted_by"
    STATUS = "status"
    PREDICTED = "predicted"

    def __str__(self) -> str:
        return str(self.value)
