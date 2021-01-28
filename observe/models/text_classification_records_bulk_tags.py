from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset


@attr.s(auto_attribs=True)
class TextClassificationRecordsBulkTags:
    """  """

    additional_properties: Dict[str, str] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TextClassificationRecordsBulkTags":
        d = src_dict.copy()
        text_classification_records_bulk_tags = TextClassificationRecordsBulkTags()

        text_classification_records_bulk_tags.additional_properties = d
        return text_classification_records_bulk_tags

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> str:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
