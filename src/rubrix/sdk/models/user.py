from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="User")


@attr.s(auto_attribs=True)
class User:
    """ Base user model """

    username: str
    email: Union[Unset, str] = UNSET
    full_name: Union[Unset, str] = UNSET
    disabled: Union[Unset, bool] = UNSET
    user_groups: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        username = self.username
        email = self.email
        full_name = self.full_name
        disabled = self.disabled
        user_groups: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.user_groups, Unset):
            user_groups = self.user_groups

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
            }
        )
        if email is not UNSET:
            field_dict["email"] = email
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if user_groups is not UNSET:
            field_dict["user_groups"] = user_groups

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        username = d.pop("username")

        email = d.pop("email", UNSET)

        full_name = d.pop("full_name", UNSET)

        disabled = d.pop("disabled", UNSET)

        user_groups = cast(List[str], d.pop("user_groups", UNSET))

        user = cls(
            username=username,
            email=email,
            full_name=full_name,
            disabled=disabled,
            user_groups=user_groups,
        )

        user.additional_properties = d
        return user

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
