from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="ErrorMessage")


@attr.s(auto_attribs=True)
class ErrorMessage:
    """Generic error class. This class is needed only for openapi documentation
    purposes.

    If some field in additional http errors changes, these changes
    should be reflected in the error model.

    Attributes:
    -----------

    detail:
        The error message"""

    detail: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        detail = self.detail

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "detail": detail,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        detail = d.pop("detail")

        error_message = cls(
            detail=detail,
        )

        error_message.additional_properties = d
        return error_message

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
