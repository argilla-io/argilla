from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset


@attr.s(auto_attribs=True)
class TokenAttributionsAttributions:
    """  """

    additional_properties: Dict[str, float] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TokenAttributionsAttributions":
        d = src_dict.copy()
        token_attributions_attributions = TokenAttributionsAttributions()

        token_attributions_attributions.additional_properties = d
        return token_attributions_attributions

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> float:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: float) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
