from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.class_prediction import ClassPrediction

T = TypeVar("T", bound="TextClassificationAnnotation")


@attr.s(auto_attribs=True)
class TextClassificationAnnotation:
    """Annotation class for text classification tasks

    Attributes:
    -----------

    labels: List[LabelPrediction]
        list of annotated labels with score"""

    agent: str
    labels: List[ClassPrediction]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        agent = self.agent
        labels = []
        for labels_item_data in self.labels:
            labels_item = labels_item_data.to_dict()

            labels.append(labels_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent": agent,
                "labels": labels,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        agent = d.pop("agent")

        labels = []
        _labels = d.pop("labels")
        for labels_item_data in _labels:
            labels_item = ClassPrediction.from_dict(labels_item_data)

            labels.append(labels_item)

        text_classification_annotation = cls(
            agent=agent,
            labels=labels,
        )

        text_classification_annotation.additional_properties = d
        return text_classification_annotation

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
