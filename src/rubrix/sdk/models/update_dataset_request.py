from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.update_dataset_request_metadata import UpdateDatasetRequestMetadata
from ..models.update_dataset_request_tags import UpdateDatasetRequestTags
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateDatasetRequest")


@attr.s(auto_attribs=True)
class UpdateDatasetRequest:
    """Modifiable fields for dataset

    Attributes:
    -----------
    tags:
        Dataset tags used for better organize or classify information
    metadata:
        Extra information that could be interested to include"""

    tags: Union[UpdateDatasetRequestTags, Unset] = UNSET
    metadata: Union[UpdateDatasetRequestMetadata, Unset] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        tags: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tags is not UNSET:
            field_dict["tags"] = tags
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        tags: Union[UpdateDatasetRequestTags, Unset] = UNSET
        _tags = d.pop("tags", UNSET)
        if not isinstance(_tags, Unset):
            tags = UpdateDatasetRequestTags.from_dict(_tags)

        metadata: Union[UpdateDatasetRequestMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if not isinstance(_metadata, Unset):
            metadata = UpdateDatasetRequestMetadata.from_dict(_metadata)

        update_dataset_request = cls(
            tags=tags,
            metadata=metadata,
        )

        update_dataset_request.additional_properties = d
        return update_dataset_request

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
