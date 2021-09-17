#  coding=utf-8
#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.sortable_field import SortableField
from ..models.text2_text_query import Text2TextQuery
from ..types import UNSET, Unset

T = TypeVar("T", bound="Text2TextSearchRequest")


@attr.s(auto_attribs=True)
class Text2TextSearchRequest:
    """API SearchRequest request

    Attributes:
    -----------

    query: Text2TextQuery
        The search query configuration

    sort:
        The sort order list"""

    query: Union[Text2TextQuery, Unset] = UNSET
    sort: Union[Unset, List[SortableField]] = UNSET
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

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        query: Union[Text2TextQuery, Unset] = UNSET
        _query = d.pop("query", UNSET)
        if not isinstance(_query, Unset):
            query = Text2TextQuery.from_dict(_query)

        sort = []
        _sort = d.pop("sort", UNSET)
        for sort_item_data in _sort or []:
            sort_item = SortableField.from_dict(sort_item_data)

            sort.append(sort_item)

        text2_text_search_request = cls(
            query=query,
            sort=sort,
        )

        text2_text_search_request.additional_properties = d
        return text2_text_search_request

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
