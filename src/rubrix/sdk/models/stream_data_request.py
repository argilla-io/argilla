from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="StreamDataRequest")


@attr.s(auto_attribs=True)
class StreamDataRequest:
    """Request data for scan dataset endpoint

    Attributes:
    -----------

    ids:
        The list of record ids to scan"""

    ids: Union[Unset, List[Union[str, int]]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.ids, Unset):
            ids = []
            for ids_item_data in self.ids:
                ids_item = ids_item_data

                ids.append(ids_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ids is not UNSET:
            field_dict["ids"] = ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ids = []
        _ids = d.pop("ids", UNSET)
        for ids_item_data in _ids or []:

            def _parse_ids_item(data: Any) -> Union[str, int]:
                data = None if isinstance(data, Unset) else data
                ids_item: Union[str, int]
                return cast(Union[str, int], data)

            ids_item = _parse_ids_item(ids_item_data)

            ids.append(ids_item)

        stream_data_request = cls(
            ids=ids,
        )

        stream_data_request.additional_properties = d
        return stream_data_request

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
