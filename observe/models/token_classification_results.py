from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from ..models.token_classification_record_out import TokenClassificationRecordOUT
from typing import cast, List
from ..models.token_classification_aggregations import TokenClassificationAggregations
from ..types import UNSET, Unset
from typing import cast
from typing import Dict
from typing import Union


@attr.s(auto_attribs=True)
class TokenClassificationResults:
    """  """

    total: Union[Unset, int] = 0
    records: Union[Unset, List[TokenClassificationRecordOUT]] = UNSET
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

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TokenClassificationResults":
        d = src_dict.copy()
        total = d.pop("total", UNSET)

        records = []
        _records = d.pop("records", UNSET)
        for records_item_data in _records or []:
            records_item = TokenClassificationRecordOUT.from_dict(records_item_data)

            records.append(records_item)

        aggregations: Union[TokenClassificationAggregations, Unset] = UNSET
        _aggregations = d.pop("aggregations", UNSET)
        if _aggregations is not None and not isinstance(_aggregations, Unset):
            aggregations = TokenClassificationAggregations.from_dict(cast(Dict[str, Any], _aggregations))

        token_classification_results = TokenClassificationResults(
            total=total, records=records, aggregations=aggregations,
        )

        token_classification_results.additional_properties = d
        return token_classification_results

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
