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

from ..models.text2_text_search_aggregations_annotated_by import (
    Text2TextSearchAggregationsAnnotatedBy,
)
from ..models.text2_text_search_aggregations_annotated_text import (
    Text2TextSearchAggregationsAnnotatedText,
)
from ..models.text2_text_search_aggregations_metadata import (
    Text2TextSearchAggregationsMetadata,
)
from ..models.text2_text_search_aggregations_predicted import (
    Text2TextSearchAggregationsPredicted,
)
from ..models.text2_text_search_aggregations_predicted_by import (
    Text2TextSearchAggregationsPredictedBy,
)
from ..models.text2_text_search_aggregations_predicted_text import (
    Text2TextSearchAggregationsPredictedText,
)
from ..models.text2_text_search_aggregations_score import (
    Text2TextSearchAggregationsScore,
)
from ..models.text2_text_search_aggregations_status import (
    Text2TextSearchAggregationsStatus,
)
from ..models.text2_text_search_aggregations_words import (
    Text2TextSearchAggregationsWords,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="Text2TextSearchAggregations")


@attr.s(auto_attribs=True)
class Text2TextSearchAggregations:
    """API for result aggregations

    Attributes:
    -----------
    words: Dict[str, int]
        The word cloud aggregations for input text
    predicted_text: Dict[str, int]
        The word cloud aggregations for predicted text
    annotated_text: Dict[str, int]
        The word cloud aggregations for annotated text
    annotated_by: Dict[str, int]
        Occurrence info about more relevant annotation agent terms
    predicted_by: Dict[str, int]
        Occurrence info about more relevant prediction agent terms
    status: Dict[str, int]
        Occurrence info about task status
    predicted: Dict[str, int]
        Occurrence info about task prediction status
    metadata: Dict[str, Dict[str, int]]
        The metadata fields aggregations"""

    words: Union[Text2TextSearchAggregationsWords, Unset] = UNSET
    predicted_text: Union[Text2TextSearchAggregationsPredictedText, Unset] = UNSET
    annotated_text: Union[Text2TextSearchAggregationsAnnotatedText, Unset] = UNSET
    annotated_by: Union[Text2TextSearchAggregationsAnnotatedBy, Unset] = UNSET
    predicted_by: Union[Text2TextSearchAggregationsPredictedBy, Unset] = UNSET
    status: Union[Text2TextSearchAggregationsStatus, Unset] = UNSET
    predicted: Union[Text2TextSearchAggregationsPredicted, Unset] = UNSET
    score: Union[Text2TextSearchAggregationsScore, Unset] = UNSET
    metadata: Union[Text2TextSearchAggregationsMetadata, Unset] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        words: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.words, Unset):
            words = self.words.to_dict()

        predicted_text: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.predicted_text, Unset):
            predicted_text = self.predicted_text.to_dict()

        annotated_text: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.annotated_text, Unset):
            annotated_text = self.annotated_text.to_dict()

        annotated_by: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.annotated_by, Unset):
            annotated_by = self.annotated_by.to_dict()

        predicted_by: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.predicted_by, Unset):
            predicted_by = self.predicted_by.to_dict()

        status: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.to_dict()

        predicted: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.predicted, Unset):
            predicted = self.predicted.to_dict()

        score: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.score, Unset):
            score = self.score.to_dict()

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if words is not UNSET:
            field_dict["words"] = words
        if predicted_text is not UNSET:
            field_dict["predicted_text"] = predicted_text
        if annotated_text is not UNSET:
            field_dict["annotated_text"] = annotated_text
        if annotated_by is not UNSET:
            field_dict["annotated_by"] = annotated_by
        if predicted_by is not UNSET:
            field_dict["predicted_by"] = predicted_by
        if status is not UNSET:
            field_dict["status"] = status
        if predicted is not UNSET:
            field_dict["predicted"] = predicted
        if score is not UNSET:
            field_dict["score"] = score
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        words: Union[Text2TextSearchAggregationsWords, Unset] = UNSET
        _words = d.pop("words", UNSET)
        if not isinstance(_words, Unset):
            words = Text2TextSearchAggregationsWords.from_dict(_words)

        predicted_text: Union[Text2TextSearchAggregationsPredictedText, Unset] = UNSET
        _predicted_text = d.pop("predicted_text", UNSET)
        if not isinstance(_predicted_text, Unset):
            predicted_text = Text2TextSearchAggregationsPredictedText.from_dict(
                _predicted_text
            )

        annotated_text: Union[Text2TextSearchAggregationsAnnotatedText, Unset] = UNSET
        _annotated_text = d.pop("annotated_text", UNSET)
        if not isinstance(_annotated_text, Unset):
            annotated_text = Text2TextSearchAggregationsAnnotatedText.from_dict(
                _annotated_text
            )

        annotated_by: Union[Text2TextSearchAggregationsAnnotatedBy, Unset] = UNSET
        _annotated_by = d.pop("annotated_by", UNSET)
        if not isinstance(_annotated_by, Unset):
            annotated_by = Text2TextSearchAggregationsAnnotatedBy.from_dict(
                _annotated_by
            )

        predicted_by: Union[Text2TextSearchAggregationsPredictedBy, Unset] = UNSET
        _predicted_by = d.pop("predicted_by", UNSET)
        if not isinstance(_predicted_by, Unset):
            predicted_by = Text2TextSearchAggregationsPredictedBy.from_dict(
                _predicted_by
            )

        status: Union[Text2TextSearchAggregationsStatus, Unset] = UNSET
        _status = d.pop("status", UNSET)
        if not isinstance(_status, Unset):
            status = Text2TextSearchAggregationsStatus.from_dict(_status)

        predicted: Union[Text2TextSearchAggregationsPredicted, Unset] = UNSET
        _predicted = d.pop("predicted", UNSET)
        if not isinstance(_predicted, Unset):
            predicted = Text2TextSearchAggregationsPredicted.from_dict(_predicted)

        score: Union[Text2TextSearchAggregationsScore, Unset] = UNSET
        _score = d.pop("score", UNSET)
        if not isinstance(_score, Unset):
            score = Text2TextSearchAggregationsScore.from_dict(_score)

        metadata: Union[Text2TextSearchAggregationsMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if not isinstance(_metadata, Unset):
            metadata = Text2TextSearchAggregationsMetadata.from_dict(_metadata)

        text2_text_search_aggregations = cls(
            words=words,
            predicted_text=predicted_text,
            annotated_text=annotated_text,
            annotated_by=annotated_by,
            predicted_by=predicted_by,
            status=status,
            predicted=predicted,
            score=score,
            metadata=metadata,
        )

        text2_text_search_aggregations.additional_properties = d
        return text2_text_search_aggregations

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
