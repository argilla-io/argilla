from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.text_classification_record import TextClassificationRecord
from ..models.text_classification_records_bulk_metadata import (
    TextClassificationRecordsBulkMetadata,
)
from ..models.text_classification_records_bulk_tags import (
    TextClassificationRecordsBulkTags,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="TextClassificationRecordsBulk")


@attr.s(auto_attribs=True)
class TextClassificationRecordsBulk:
    """API backward compatibility data model for bulk record old endpoint

    Attributes:
    -----------

    name:str
        The dataset name"""

    records: List[TextClassificationRecord]
    name: str
    tags: Union[TextClassificationRecordsBulkTags, Unset] = UNSET
    metadata: Union[TextClassificationRecordsBulkMetadata, Unset] = UNSET
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
            records_item = TextClassificationRecord.from_dict(records_item_data)

            records.append(records_item)

        name = d.pop("name")

        tags: Union[TextClassificationRecordsBulkTags, Unset] = UNSET
        _tags = d.pop("tags", UNSET)
        if not isinstance(_tags, Unset):
            tags = TextClassificationRecordsBulkTags.from_dict(_tags)

        metadata: Union[TextClassificationRecordsBulkMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if not isinstance(_metadata, Unset):
            metadata = TextClassificationRecordsBulkMetadata.from_dict(_metadata)

        text_classification_records_bulk = cls(
            records=records,
            name=name,
            tags=tags,
            metadata=metadata,
        )

        text_classification_records_bulk.additional_properties = d
        return text_classification_records_bulk

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
