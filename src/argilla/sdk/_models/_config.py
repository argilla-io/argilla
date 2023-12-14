import dataclasses
from typing import List

from ._fields import Field
from ._questions import Question

__all__ = ["DatasetConfiguration"]

@dataclasses.dataclass
class DatasetConfiguration:
    guidelines: str
    allow_extra_metadata: bool = True

    fields: List[Field] = dataclasses.field(default_factory=list)
    questions: List[Question] = dataclasses.field(default_factory=list)

    def validate(self):
        for field in self.fields:
            field.validate()

        for question in self.questions:
            question.validate()

    def to_dict(self):
        return {
            "guidelines": self.guidelines,
            "allow_extra_metadata": self.allow_extra_metadata,
            "fields": [f.to_dict() for f in self.fields],
            "questions": [q.to_dict() for q in self.questions],
        }
