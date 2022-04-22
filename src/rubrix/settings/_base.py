from dataclasses import dataclass
from typing import Any, Dict, Optional, Set


@dataclass
class AbstractSettings:
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AbstractSettings":
        raise NotImplementedError()


@dataclass
class LabelSchema(object):

    id: str
    name: str
    description: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            self.id = self.name

    def __hash__(self):
        return hash(self.id)


@dataclass
class LabelsSchema:
    labels: Set[LabelSchema]

    @classmethod
    def from_labels_set(cls, labels_schema: Set[str]):
        return cls(
            labels={LabelSchema(id=label, name=label) for label in labels_schema}
        )
