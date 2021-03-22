from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Union
from typing import Dict
from ..models.token_classification_sort_param import TokenClassificationSortParam
from typing import cast, List
from ..types import UNSET, Unset
from ..models.token_classification_query import TokenClassificationQuery
from typing import cast


@attr.s(auto_attribs=True)
class TokenClassificationSearchRequest:
    """ Base search query request """

    query: Union[TokenClassificationQuery, Unset] = UNSET
    sort: Union[Unset, List[TokenClassificationSortParam]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        query: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.query, Unset):
            query = self.query.to_dict()

        sort: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.sort, Unset):
            sort = []
            for sort_item_data in self.sort:
                sort_item = sort_item_data.to_dict()

                sort.append(sort_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if query is not UNSET:
            field_dict["query"] = query
        if sort is not UNSET:
            field_dict["sort"] = sort

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TokenClassificationSearchRequest":
        d = src_dict.copy()
        query: Union[TokenClassificationQuery, Unset] = UNSET
        _query = d.pop("query", UNSET)
        if _query is not None and not isinstance(_query, Unset):
            query = TokenClassificationQuery.from_dict(cast(Dict[str, Any], _query))

        sort = []
        _sort = d.pop("sort", UNSET)
        for sort_item_data in _sort or []:
            sort_item = TokenClassificationSortParam.from_dict(sort_item_data)

            sort.append(sort_item)

        token_classification_search_request = TokenClassificationSearchRequest(query=query, sort=sort,)

        token_classification_search_request.additional_properties = d
        return token_classification_search_request

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
