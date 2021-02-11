from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Union
from typing import Dict
from ..types import UNSET, Unset
from typing import cast, List
from ..models.validation_error import ValidationError
from typing import cast


@attr.s(auto_attribs=True)
class HTTPValidationError:
    """  """

    detail: Union[Unset, List[ValidationError]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        detail: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.detail, Unset):
            detail = []
            for detail_item_data in self.detail:
                detail_item = detail_item_data.to_dict()

                detail.append(detail_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if detail is not UNSET:
            field_dict["detail"] = detail

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "HTTPValidationError":
        d = src_dict.copy()
        detail = []
        _detail = d.pop("detail", UNSET)
        for detail_item_data in _detail or []:
            detail_item = ValidationError.from_dict(detail_item_data)

            detail.append(detail_item)

        http_validation_error = HTTPValidationError(detail=detail,)

        http_validation_error.additional_properties = d
        return http_validation_error

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
