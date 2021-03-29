from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.token_attributions_attributions import TokenAttributionsAttributions
from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenAttributions")


@attr.s(auto_attribs=True)
class TokenAttributions:
    """The token attributions explaining predicted labels

    Attributes:
    -----------

    token: str
        The input token
    attributions: Dict[str, float]
        A dictionary containing label class-attribution pairs"""

    token: str
    attributions: Union[TokenAttributionsAttributions, Unset] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        token = self.token
        attributions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attributions, Unset):
            attributions = self.attributions.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "token": token,
            }
        )
        if attributions is not UNSET:
            field_dict["attributions"] = attributions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        token = d.pop("token")

        attributions: Union[TokenAttributionsAttributions, Unset] = UNSET
        _attributions = d.pop("attributions", UNSET)
        if not isinstance(_attributions, Unset):
            attributions = TokenAttributionsAttributions.from_dict(_attributions)

        token_attributions = cls(
            token=token,
            attributions=attributions,
        )

        token_attributions.additional_properties = d
        return token_attributions

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
