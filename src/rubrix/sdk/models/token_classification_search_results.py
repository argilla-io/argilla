from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.token_classification_aggregations import TokenClassificationAggregations
from ..models.token_classification_record import TokenClassificationRecord
from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenClassificationSearchResults")


@attr.s(auto_attribs=True)
class TokenClassificationSearchResults:
    """API search results

    Attributes:
    -----------

    total: int
        The total number of records
    records: List[TokenClassificationRecord]
        The selected records to return
    aggregations: TokenClassificationAggregations
        SearchRequest aggregations (if no pagination)"""

    total: Union[Unset, int] = 0
    records: Union[Unset, List[TokenClassificationRecord]] = UNSET
    aggregations: Union[TokenClassificationAggregations, Unset] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        total = self.total
        records: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.records, Unset):
            records = []
            for records_item_data in self.records:
                records_item = records_item_data.to_dict()

                records.append(records_item)

        aggregations: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.aggregations, Unset):
            aggregations = self.aggregations.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total is not UNSET:
            field_dict["total"] = total
        if records is not UNSET:
            field_dict["records"] = records
        if aggregations is not UNSET:
            field_dict["aggregations"] = aggregations

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        total = d.pop("total", UNSET)

        records = []
        _records = d.pop("records", UNSET)
        for records_item_data in _records or []:
            records_item = TokenClassificationRecord.from_dict(records_item_data)

            records.append(records_item)

        aggregations: Union[TokenClassificationAggregations, Unset] = UNSET
        _aggregations = d.pop("aggregations", UNSET)
        if not isinstance(_aggregations, Unset):
            aggregations = TokenClassificationAggregations.from_dict(_aggregations)

        token_classification_search_results = cls(
            total=total,
            records=records,
            aggregations=aggregations,
        )

        token_classification_search_results.additional_properties = d
        return token_classification_search_results

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
