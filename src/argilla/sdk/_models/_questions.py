import dataclasses
from typing import Optional
from uuid import UUID

from argilla.sdk._api import *

__all__ = ["Question", "QuestionSettings", "RatingQuestionSettings", "LabelQuestionSettings"]


@dataclasses.dataclass
class Question:
    name: str
    title: str
    settings: QuestionSettings
    description: Optional[str] = None
    required: bool = True

    id: Optional[UUID] = None

    def validate(self):
        pass

    def to_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "required": self.required,
            "settings": self.settings.to_dict(),
        }
