from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from ..models.sortable_field import SortableField
from ..models.sort_order import SortOrder
from typing import Union
from ..types import UNSET, Unset
from typing import cast, Union


@attr.s(auto_attribs=True)
class TokenClassificationSortParam:
    """  """

    by: Union[SortableField, str]
    order: Union[Unset, SortOrder] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        if isinstance(self.by, SortableField):
            by = self.by.value

        else:
            by = self.by

        order: Union[Unset, SortOrder] = UNSET
        if not isinstance(self.order, Unset):
            order = self.order

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {"by": by,}
        )
        if order is not UNSET:
            field_dict["order"] = order

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TokenClassificationSortParam":
        d = src_dict.copy()

        def _parse_by(data: Any) -> Union[SortableField, str]:
            data = None if isinstance(data, Unset) else data
            by: Union[SortableField, str]
            try:
                by = SortableField(data)

                return by
            except:  # noqa: E722
                pass
            return cast(Union[SortableField, str], data)

        by = _parse_by(d.pop("by"))

        order = None
        _order = d.pop("order", UNSET)
        if _order is not None and not isinstance((_order), Unset):
            order = SortOrder(_order)

        token_classification_sort_param = TokenClassificationSortParam(by=by, order=order,)

        token_classification_sort_param.additional_properties = d
        return token_classification_sort_param

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
