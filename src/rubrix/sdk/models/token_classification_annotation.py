from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.entity_span import EntitySpan
from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenClassificationAnnotation")


@attr.s(auto_attribs=True)
class TokenClassificationAnnotation:
    """Annotation class for rToken classification problem

    Attributes:
    -----------
    entities: List[EntitiesSpan]
        a list of detected entities spans in tokenized text, if any.
    score: float
        score related to annotated entities. The higher is score value, the
        more likely is that entities were properly annotated."""

    agent: str
    entities: Union[Unset, List[EntitySpan]] = UNSET
    score: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        agent = self.agent
        entities: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.entities, Unset):
            entities = []
            for entities_item_data in self.entities:
                entities_item = entities_item_data.to_dict()

                entities.append(entities_item)

        score = self.score

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent": agent,
            }
        )
        if entities is not UNSET:
            field_dict["entities"] = entities
        if score is not UNSET:
            field_dict["score"] = score

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        agent = d.pop("agent")

        entities = []
        _entities = d.pop("entities", UNSET)
        for entities_item_data in _entities or []:
            entities_item = EntitySpan.from_dict(entities_item_data)

            entities.append(entities_item)

        score = d.pop("score", UNSET)

        token_classification_annotation = cls(
            agent=agent,
            entities=entities,
            score=score,
        )

        token_classification_annotation.additional_properties = d
        return token_classification_annotation

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
