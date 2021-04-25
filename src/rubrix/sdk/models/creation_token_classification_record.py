import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.creation_token_classification_record_metadata import (
    CreationTokenClassificationRecordMetadata,
)
from ..models.task_status import TaskStatus
from ..models.token_classification_annotation import TokenClassificationAnnotation
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreationTokenClassificationRecord")


@attr.s(auto_attribs=True)
class CreationTokenClassificationRecord:
    """Dataset record for token classification task

    Attributes:
    -----------

    tokens: List[str]
        The input tokens
    text: str
        Textual representation of token list"""

    tokens: List[str]
    raw_text: str
    id: Union[Unset, int, str] = UNSET
    metadata: Union[CreationTokenClassificationRecordMetadata, Unset] = UNSET
    event_timestamp: Union[Unset, datetime.datetime] = UNSET
    status: Union[Unset, TaskStatus] = UNSET
    prediction: Union[TokenClassificationAnnotation, Unset] = UNSET
    annotation: Union[TokenClassificationAnnotation, Unset] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        tokens = self.tokens

        raw_text = self.raw_text
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

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tokens": tokens,
                "raw_text": raw_text,
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

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        tokens = cast(List[str], d.pop("tokens"))

        raw_text = d.pop("raw_text")

        def _parse_id(data: Any) -> Union[Unset, int, str]:
            data = None if isinstance(data, Unset) else data
            id: Union[Unset, int, str]
            return cast(Union[Unset, int, str], data)

        id = _parse_id(d.pop("id", UNSET))

        metadata: Union[CreationTokenClassificationRecordMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if not isinstance(_metadata, Unset):
            metadata = CreationTokenClassificationRecordMetadata.from_dict(_metadata)

        event_timestamp: Union[Unset, datetime.datetime] = UNSET
        _event_timestamp = d.pop("event_timestamp", UNSET)
        if not isinstance(_event_timestamp, Unset):
            event_timestamp = isoparse(_event_timestamp)

        status: Union[Unset, TaskStatus] = UNSET
        _status = d.pop("status", UNSET)
        if not isinstance(_status, Unset):
            status = TaskStatus(_status)

        prediction: Union[TokenClassificationAnnotation, Unset] = UNSET
        _prediction = d.pop("prediction", UNSET)
        if not isinstance(_prediction, Unset):
            prediction = TokenClassificationAnnotation.from_dict(_prediction)

        annotation: Union[TokenClassificationAnnotation, Unset] = UNSET
        _annotation = d.pop("annotation", UNSET)
        if not isinstance(_annotation, Unset):
            annotation = TokenClassificationAnnotation.from_dict(_annotation)

        creation_token_classification_record = cls(
            tokens=tokens,
            raw_text=raw_text,
            id=id,
            metadata=metadata,
            event_timestamp=event_timestamp,
            status=status,
            prediction=prediction,
            annotation=annotation,
        )

        creation_token_classification_record.additional_properties = d
        return creation_token_classification_record

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
