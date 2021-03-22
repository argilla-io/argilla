from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union


@attr.s(auto_attribs=True)
class BulkResponse:
    """  """

    dataset: str
    processed: int
    failed: Union[Unset, int] = 0
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataset = self.dataset
        processed = self.processed
        failed = self.failed

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {"dataset": dataset, "processed": processed,}
        )
        if failed is not UNSET:
            field_dict["failed"] = failed

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "BulkResponse":
        d = src_dict.copy()
        dataset = d.pop("dataset")

        processed = d.pop("processed")

        failed = d.pop("failed", UNSET)

        bulk_response = BulkResponse(dataset=dataset, processed=processed, failed=failed,)

        bulk_response.additional_properties = d
        return bulk_response

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
