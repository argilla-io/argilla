import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.creation_text_classification_record_explanation import (
    CreationTextClassificationRecordExplanation,
)
from ..models.creation_text_classification_record_inputs import (
    CreationTextClassificationRecordInputs,
)
from ..models.creation_text_classification_record_metadata import (
    CreationTextClassificationRecordMetadata,
)
from ..models.task_status import TaskStatus
from ..models.text_classification_annotation import TextClassificationAnnotation
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreationTextClassificationRecord")


@attr.s(auto_attribs=True)
class CreationTextClassificationRecord:
    """Text classification record

    Attributes:
    -----------

    inputs: Dict[str, Union[str, List[str]]]
        The input data text

    multi_label: bool
        Enable text classification with multiple predicted/annotated labels.
        Default=False

    explanation: Dict[str, List[TokenAttributions]]
        Token attribution list explaining predicted classes per token input.
        The dictionary key must be aligned with provided record text. Optional"""

    inputs: CreationTextClassificationRecordInputs
    id: Union[Unset, int, str] = UNSET
    metadata: Union[CreationTextClassificationRecordMetadata, Unset] = UNSET
    event_timestamp: Union[Unset, datetime.datetime] = UNSET
    status: Union[Unset, TaskStatus] = UNSET
    prediction: Union[TextClassificationAnnotation, Unset] = UNSET
    annotation: Union[TextClassificationAnnotation, Unset] = UNSET
    multi_label: Union[Unset, bool] = False
    explanation: Union[CreationTextClassificationRecordExplanation, Unset] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        inputs = self.inputs.to_dict()

        id: Union[Unset, int, str]
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        event_timestamp: Union[Unset, str] = UNSET
        if not isinstance(self.event_timestamp, Unset):
            event_timestamp = self.event_timestamp.isoformat()

        status: Union[Unset, TaskStatus] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        prediction: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.prediction, Unset):
            prediction = self.prediction.to_dict()

        annotation: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.annotation, Unset):
            annotation = self.annotation.to_dict()

        multi_label = self.multi_label
        explanation: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.explanation, Unset):
            explanation = self.explanation.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inputs": inputs,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if event_timestamp is not UNSET:
            field_dict["event_timestamp"] = event_timestamp
        if status is not UNSET:
            field_dict["status"] = status
        if prediction is not UNSET:
            field_dict["prediction"] = prediction
        if annotation is not UNSET:
            field_dict["annotation"] = annotation
        if multi_label is not UNSET:
            field_dict["multi_label"] = multi_label
        if explanation is not UNSET:
            field_dict["explanation"] = explanation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        inputs = CreationTextClassificationRecordInputs.from_dict(d.pop("inputs"))

        def _parse_id(data: Any) -> Union[Unset, int, str]:
            data = None if isinstance(data, Unset) else data
            id: Union[Unset, int, str]
            return cast(Union[Unset, int, str], data)

        id = _parse_id(d.pop("id", UNSET))

        metadata: Union[CreationTextClassificationRecordMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if not isinstance(_metadata, Unset):
            metadata = CreationTextClassificationRecordMetadata.from_dict(_metadata)

        event_timestamp: Union[Unset, datetime.datetime] = UNSET
        _event_timestamp = d.pop("event_timestamp", UNSET)
        if not isinstance(_event_timestamp, Unset):
            event_timestamp = isoparse(_event_timestamp)

        status: Union[Unset, TaskStatus] = UNSET
        _status = d.pop("status", UNSET)
        if not isinstance(_status, Unset):
            status = TaskStatus(_status)

        prediction: Union[TextClassificationAnnotation, Unset] = UNSET
        _prediction = d.pop("prediction", UNSET)
        if not isinstance(_prediction, Unset):
            prediction = TextClassificationAnnotation.from_dict(_prediction)

        annotation: Union[TextClassificationAnnotation, Unset] = UNSET
        _annotation = d.pop("annotation", UNSET)
        if not isinstance(_annotation, Unset):
            annotation = TextClassificationAnnotation.from_dict(_annotation)

        multi_label = d.pop("multi_label", UNSET)

        explanation: Union[CreationTextClassificationRecordExplanation, Unset] = UNSET
        _explanation = d.pop("explanation", UNSET)
        if not isinstance(_explanation, Unset):
            explanation = CreationTextClassificationRecordExplanation.from_dict(
                _explanation
            )

        creation_text_classification_record = cls(
            inputs=inputs,
            id=id,
            metadata=metadata,
            event_timestamp=event_timestamp,
            status=status,
            prediction=prediction,
            annotation=annotation,
            multi_label=multi_label,
            explanation=explanation,
        )

        creation_text_classification_record.additional_properties = d
        return creation_text_classification_record

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
