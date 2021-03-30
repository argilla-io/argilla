import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="DatasetSnapshot")


@attr.s(auto_attribs=True)
class DatasetSnapshot:
    """ Complete data model for dataset snapshot. """

    id: str
    uri: str
    task: str
    creation_date: datetime.datetime
    format: Union[Unset, str] = "json"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        uri = self.uri
        task = self.task
        creation_date = self.creation_date.isoformat()

        format = self.format

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "uri": uri,
                "task": task,
                "creation_date": creation_date,
            }
        )
        if format is not UNSET:
            field_dict["format"] = format

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        uri = d.pop("uri")

        task = d.pop("task")

        creation_date = isoparse(d.pop("creation_date"))

        format = d.pop("format", UNSET)

        dataset_snapshot = cls(
            id=id,
            uri=uri,
            task=task,
            creation_date=creation_date,
            format=format,
        )

        dataset_snapshot.additional_properties = d
        return dataset_snapshot

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
