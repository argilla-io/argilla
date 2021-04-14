from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="EntitySpan")


@attr.s(auto_attribs=True)
class EntitySpan:
    """The tokens span for a labeled text.

    Entity spans will be defined between from start to end - 1

    Attributes:
    -----------

    start: int
        character start position
    end: int
        character end position, must be higher than the starting character.
    start_token: Optional[int]
        start token for entity span. Optional
    end_token: Optional[int]
        end token for entity span, must be higher than the starting token position. Optional
    label: str
        the label related to tokens that conforms the entity span"""

    start: int
    end: int
    label: str
    start_token: Union[Unset, int] = UNSET
    end_token: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        start = self.start
        end = self.end
        label = self.label
        start_token = self.start_token
        end_token = self.end_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "start": start,
                "end": end,
                "label": label,
            }
        )
        if start_token is not UNSET:
            field_dict["start_token"] = start_token
        if end_token is not UNSET:
            field_dict["end_token"] = end_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        start = d.pop("start")

        end = d.pop("end")

        label = d.pop("label")

        start_token = d.pop("start_token", UNSET)

        end_token = d.pop("end_token", UNSET)

        entity_span = cls(
            start=start,
            end=end,
            label=label,
            start_token=start_token,
            end_token=end_token,
        )

        entity_span.additional_properties = d
        return entity_span

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
