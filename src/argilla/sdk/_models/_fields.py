import dataclasses
from typing import Optional
from uuid import UUID

from argilla.sdk._api import TextFieldSettings

__all__ = ["Field", "TextFieldSettings"]


@dataclasses.dataclass
class Field:
    name: str
    title: str
    required: bool = True
    settings: TextFieldSettings = dataclasses.field(default_factory=TextFieldSettings)

    id: Optional[UUID] = None

    def validate(self):
        pass

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "required": self.required,
            "settings": self.settings.to_dict(),
        }
