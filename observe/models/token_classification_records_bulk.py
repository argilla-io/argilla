from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from ..models.token_classification_records_bulk_metadata import TokenClassificationRecordsBulkMetadata
from typing import Union
from ..models.token_classification_records_bulk_tags import TokenClassificationRecordsBulkTags
from typing import Dict
from typing import cast, List
from ..models.token_classification_record import TokenClassificationRecord
from ..types import UNSET, Unset
from typing import cast


@attr.s(auto_attribs=True)
class TokenClassificationRecordsBulk:
    """ Class for log records in bulk mode """

    name: str
    records: List[TokenClassificationRecord]
    tags: Union[TokenClassificationRecordsBulkTags, Unset] = UNSET
    metadata: Union[TokenClassificationRecordsBulkMetadata, Unset] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        records = []
        for records_item_data in self.records:
            records_item = records_item_data.to_dict()

            records.append(records_item)

        tags: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {"name": name, "records": records,}
        )
        if tags is not UNSET:
            field_dict["tags"] = tags
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TokenClassificationRecordsBulk":
        d = src_dict.copy()
        name = d.pop("name")

        records = []
        _records = d.pop("records")
        for records_item_data in _records:
            records_item = TokenClassificationRecord.from_dict(records_item_data)

            records.append(records_item)

        tags: Union[TokenClassificationRecordsBulkTags, Unset] = UNSET
        _tags = d.pop("tags", UNSET)
        if _tags is not None and not isinstance(_tags, Unset):
            tags = TokenClassificationRecordsBulkTags.from_dict(cast(Dict[str, Any], _tags))

        metadata: Union[TokenClassificationRecordsBulkMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if _metadata is not None and not isinstance(_metadata, Unset):
            metadata = TokenClassificationRecordsBulkMetadata.from_dict(cast(Dict[str, Any], _metadata))

        token_classification_records_bulk = TokenClassificationRecordsBulk(
            name=name, records=records, tags=tags, metadata=metadata,
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
