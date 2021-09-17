#  coding=utf-8
#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.dataset_metadata import DatasetMetadata
from ..models.dataset_tags import DatasetTags
from ..models.task_type import TaskType
from ..types import UNSET, Unset

T = TypeVar("T", bound="Dataset")


@attr.s(auto_attribs=True)
class Dataset:
    """Dataset used for response output"""

    name: str
    task: TaskType
    tags: Union[DatasetTags, Unset] = UNSET
    metadata: Union[DatasetMetadata, Unset] = UNSET
    owner: Union[Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    last_updated: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        task = self.task.value

        tags: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        owner = self.owner
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        last_updated: Union[Unset, str] = UNSET
        if not isinstance(self.last_updated, Unset):
            last_updated = self.last_updated.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "task": task,
            }
        )
        if tags is not UNSET:
            field_dict["tags"] = tags
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if owner is not UNSET:
            field_dict["owner"] = owner
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if last_updated is not UNSET:
            field_dict["last_updated"] = last_updated

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        task = TaskType(d.pop("task"))

        tags: Union[DatasetTags, Unset] = UNSET
        _tags = d.pop("tags", UNSET)
        if not isinstance(_tags, Unset):
            tags = DatasetTags.from_dict(_tags)

        metadata: Union[DatasetMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if not isinstance(_metadata, Unset):
            metadata = DatasetMetadata.from_dict(_metadata)

        owner = d.pop("owner", UNSET)

        created_at: Union[Unset, datetime.datetime] = UNSET
        _created_at = d.pop("created_at", UNSET)
        if not isinstance(_created_at, Unset):
            created_at = isoparse(_created_at)

        last_updated: Union[Unset, datetime.datetime] = UNSET
        _last_updated = d.pop("last_updated", UNSET)
        if not isinstance(_last_updated, Unset):
            last_updated = isoparse(_last_updated)

        dataset = cls(
            name=name,
            task=task,
            tags=tags,
            metadata=metadata,
            owner=owner,
            created_at=created_at,
            last_updated=last_updated,
        )

        dataset.additional_properties = d
        return dataset

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
