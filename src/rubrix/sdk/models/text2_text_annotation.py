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

from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.text2_text_prediction import Text2TextPrediction

T = TypeVar("T", bound="Text2TextAnnotation")


@attr.s(auto_attribs=True)
class Text2TextAnnotation:
    """Annotation class for text2text tasks

    Attributes:
    -----------

    sentences: str
        List of sentence predictions/annotations"""

    agent: str
    sentences: List[Text2TextPrediction]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        agent = self.agent
        sentences = []
        for sentences_item_data in self.sentences:
            sentences_item = sentences_item_data.to_dict()

            sentences.append(sentences_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent": agent,
                "sentences": sentences,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        agent = d.pop("agent")

        sentences = []
        _sentences = d.pop("sentences")
        for sentences_item_data in _sentences:
            sentences_item = Text2TextPrediction.from_dict(sentences_item_data)

            sentences.append(sentences_item)

        text2_text_annotation = cls(
            agent=agent,
            sentences=sentences,
        )

        text2_text_annotation.additional_properties = d
        return text2_text_annotation

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
