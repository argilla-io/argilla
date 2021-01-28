from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Union
from ..types import UNSET, Unset


@attr.s(auto_attribs=True)
class ConfidenceRange:
    """  """

    range_from: Union[Unset, float] = 0.0
    range_to: Union[Unset, float] = 1.0
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        range_from = self.range_from
        range_to = self.range_to

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if range_from is not UNSET:
            field_dict["range_from"] = range_from
        if range_to is not UNSET:
            field_dict["range_to"] = range_to

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "ConfidenceRange":
        d = src_dict.copy()
        range_from = d.pop("range_from", UNSET)

        range_to = d.pop("range_to", UNSET)

        confidence_range = ConfidenceRange(range_from=range_from, range_to=range_to,)

        confidence_range.additional_properties = d
        return confidence_range

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
