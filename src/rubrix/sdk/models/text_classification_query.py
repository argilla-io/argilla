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

from ..models.prediction_status import PredictionStatus
from ..models.score_range import ScoreRange
from ..models.task_status import TaskStatus
from ..models.text_classification_query_metadata import TextClassificationQueryMetadata
from ..types import UNSET, Unset

T = TypeVar("T", bound="TextClassificationQuery")


@attr.s(auto_attribs=True)
class TextClassificationQuery:
    """API Filters for text classification

    Attributes:
    -----------
    ids: Optional[List[Union[str, int]]]
        Record ids list

    query_text: str
        Text query over inputs
    metadata: Optional[Dict[str, Union[str, List[str]]]]
        Text query over metadata fields. Default=None

    predicted_as: List[str]
        List of predicted terms
    annotated_as: List[str]
        List of annotated terms
    annotated_by: List[str]
        List of annotation agents
    predicted_by: List[str]
        List of predicted agents
    status: List[TaskStatus]
        List of task status
    predicted: Optional[PredictionStatus]
        The task prediction status"""

    ids: Union[Unset, List[Union[str, int]]] = UNSET
    query_inputs: Union[Unset, str] = UNSET
    metadata: Union[TextClassificationQueryMetadata, Unset] = UNSET
    predicted_as: Union[Unset, List[str]] = UNSET
    annotated_as: Union[Unset, List[str]] = UNSET
    annotated_by: Union[Unset, List[str]] = UNSET
    predicted_by: Union[Unset, List[str]] = UNSET
    score: Union[ScoreRange, Unset] = UNSET
    status: Union[Unset, List[TaskStatus]] = UNSET
    predicted: Union[Unset, PredictionStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.ids, Unset):
            ids = []
            for ids_item_data in self.ids:
                ids_item = ids_item_data

                ids.append(ids_item)

        query_inputs = self.query_inputs
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        predicted_as: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.predicted_as, Unset):
            predicted_as = self.predicted_as

        annotated_as: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.annotated_as, Unset):
            annotated_as = self.annotated_as

        annotated_by: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.annotated_by, Unset):
            annotated_by = self.annotated_by

        predicted_by: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.predicted_by, Unset):
            predicted_by = self.predicted_by

        score: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.score, Unset):
            score = self.score.to_dict()

        status: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.status, Unset):
            status = []
            for status_item_data in self.status:
                status_item = status_item_data.value

                status.append(status_item)

        predicted: Union[Unset, PredictionStatus] = UNSET
        if not isinstance(self.predicted, Unset):
            predicted = self.predicted

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ids is not UNSET:
            field_dict["ids"] = ids
        if query_inputs is not UNSET:
            field_dict["query_inputs"] = query_inputs
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if predicted_as is not UNSET:
            field_dict["predicted_as"] = predicted_as
        if annotated_as is not UNSET:
            field_dict["annotated_as"] = annotated_as
        if annotated_by is not UNSET:
            field_dict["annotated_by"] = annotated_by
        if predicted_by is not UNSET:
            field_dict["predicted_by"] = predicted_by
        if score is not UNSET:
            field_dict["score"] = score
        if status is not UNSET:
            field_dict["status"] = status
        if predicted is not UNSET:
            field_dict["predicted"] = predicted

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ids = []
        _ids = d.pop("ids", UNSET)
        for ids_item_data in _ids or []:

            def _parse_ids_item(data: Any) -> Union[str, int]:
                data = None if isinstance(data, Unset) else data
                ids_item: Union[str, int]
                return cast(Union[str, int], data)

            ids_item = _parse_ids_item(ids_item_data)

            ids.append(ids_item)

        query_inputs = d.pop("query_inputs", UNSET)

        metadata: Union[TextClassificationQueryMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if not isinstance(_metadata, Unset):
            metadata = TextClassificationQueryMetadata.from_dict(_metadata)

        predicted_as = cast(List[str], d.pop("predicted_as", UNSET))

        annotated_as = cast(List[str], d.pop("annotated_as", UNSET))

        annotated_by = cast(List[str], d.pop("annotated_by", UNSET))

        predicted_by = cast(List[str], d.pop("predicted_by", UNSET))

        score: Union[ScoreRange, Unset] = UNSET
        _score = d.pop("score", UNSET)
        if not isinstance(_score, Unset):
            score = ScoreRange.from_dict(_score)

        status = []
        _status = d.pop("status", UNSET)
        for status_item_data in _status or []:
            status_item = TaskStatus(status_item_data)

            status.append(status_item)

        predicted: Union[Unset, PredictionStatus] = UNSET
        _predicted = d.pop("predicted", UNSET)
        if not isinstance(_predicted, Unset):
            predicted = PredictionStatus(_predicted)

        text_classification_query = cls(
            ids=ids,
            query_inputs=query_inputs,
            metadata=metadata,
            predicted_as=predicted_as,
            annotated_as=annotated_as,
            annotated_by=annotated_by,
            predicted_by=predicted_by,
            score=score,
            status=status,
            predicted=predicted,
        )

        text_classification_query.additional_properties = d
        return text_classification_query

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
