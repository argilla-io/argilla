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

from ..types import UNSET, Unset

T = TypeVar("T", bound="ClassPrediction")


@attr.s(auto_attribs=True)
class ClassPrediction:
    """Single class prediction

    Attributes:
    -----------

    class_label: Union[str, int]
        the predicted class

    score: float
        the predicted class score. For human-supervised annotations,
        this probability should be 1.0"""

    class_: Union[str, int]
    score: Union[Unset, float] = 1.0
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        class_ = self.class_

        score = self.score

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "class": class_,
            }
        )
        if score is not UNSET:
            field_dict["score"] = score

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_class_(data: Any) -> Union[str, int]:
            data = None if isinstance(data, Unset) else data
            class_: Union[str, int]
            return cast(Union[str, int], data)

        class_ = _parse_class_(d.pop("class"))

        score = d.pop("score", UNSET)

        class_prediction = cls(
            class_=class_,
            score=score,
        )

        class_prediction.additional_properties = d
        return class_prediction

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
