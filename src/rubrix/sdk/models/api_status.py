from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.api_status_elasticsearch import ApiStatusElasticsearch
from ..models.api_status_mem_info import ApiStatusMemInfo

T = TypeVar("T", bound="ApiStatus")


@attr.s(auto_attribs=True)
class ApiStatus:
    """ The Rubrix api status model """

    rubrix_version: str
    elasticsearch: ApiStatusElasticsearch
    mem_info: ApiStatusMemInfo
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        rubrix_version = self.rubrix_version
        elasticsearch = self.elasticsearch.to_dict()

        mem_info = self.mem_info.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rubrix_version": rubrix_version,
                "elasticsearch": elasticsearch,
                "mem_info": mem_info,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        rubrix_version = d.pop("rubrix_version")

        elasticsearch = ApiStatusElasticsearch.from_dict(d.pop("elasticsearch"))

        mem_info = ApiStatusMemInfo.from_dict(d.pop("mem_info"))

        api_status = cls(
            rubrix_version=rubrix_version,
            elasticsearch=elasticsearch,
            mem_info=mem_info,
        )

        api_status.additional_properties = d
        return api_status

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
