from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.token_classification_record import TokenClassificationRecord
from ..models.token_classification_records_bulk_metadata import (
    TokenClassificationRecordsBulkMetadata,
)
from ..models.token_classification_records_bulk_tags import (
    TokenClassificationRecordsBulkTags,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenClassificationRecordsBulk")


@attr.s(auto_attribs=True)
class TokenClassificationRecordsBulk:
    """ A API backward compatibility data model for bulk records endpoint """

    records: List[TokenClassificationRecord]
    name: str
    tags: Union[TokenClassificationRecordsBulkTags, Unset] = UNSET
    metadata: Union[TokenClassificationRecordsBulkMetadata, Unset] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        records = []
        for records_item_data in self.records:
            records_item = records_item_data.to_dict()

            records.append(records_item)

        name = self.name
        tags: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "records": records,
                "name": name,
            }
        )
        if tags is not UNSET:
            field_dict["tags"] = tags
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        records = []
        _records = d.pop("records")
        for records_item_data in _records:
            records_item = TokenClassificationRecord.from_dict(records_item_data)

            records.append(records_item)

        name = d.pop("name")

        tags: Union[TokenClassificationRecordsBulkTags, Unset] = UNSET
        _tags = d.pop("tags", UNSET)
        if not isinstance(_tags, Unset):
            tags = TokenClassificationRecordsBulkTags.from_dict(_tags)

        metadata: Union[TokenClassificationRecordsBulkMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if not isinstance(_metadata, Unset):
            metadata = TokenClassificationRecordsBulkMetadata.from_dict(_metadata)

        token_classification_records_bulk = cls(
            records=records,
            name=name,
            tags=tags,
            metadata=metadata,
        )

        token_classification_records_bulk.additional_properties = d
        return token_classification_records_bulk

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
