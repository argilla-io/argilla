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

from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import Unset

T = TypeVar("T", bound="CreationTextClassificationRecordInputs")


@attr.s(auto_attribs=True)
class CreationTextClassificationRecordInputs:
    """ """

    additional_properties: Dict[str, Union[str, List[str]]] = attr.ib(
        init=False, factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            if isinstance(prop, list):
                field_dict[prop_name] = prop

            else:
                field_dict[prop_name] = prop

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        creation_text_classification_record_inputs = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(data: Any) -> Union[str, List[str]]:
                data = None if isinstance(data, Unset) else data
                additional_property: Union[str, List[str]]
                try:
                    additional_property = cast(List[str], data)

                    return additional_property
                except:  # noqa: E722
                    pass
                return cast(Union[str, List[str]], data)

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        creation_text_classification_record_inputs.additional_properties = (
            additional_properties
        )
        return creation_text_classification_record_inputs

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Union[str, List[str]]:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Union[str, List[str]]) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
