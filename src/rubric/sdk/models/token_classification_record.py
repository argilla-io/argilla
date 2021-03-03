from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Optional
from typing import Union
from typing import Dict
from ..models.token_classification_annotation import TokenClassificationAnnotation
from typing import cast, List
import datetime
from ..models.record_status import RecordStatus
from ..models.token_classification_record_metadata import TokenClassificationRecordMetadata
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast


@attr.s(auto_attribs=True)
class TokenClassificationRecord:
    """ Data record for token classification

Attributes:
-----------

tokens: List[str]
    the tokenized text for entity annotation

prediction: TokenClassificationAnnotation
    the predicted entities for tokens

annotation: Optional[TokenClassificationAnnotation]
    the real annotation. This annotation should be generated
    by some human-supervised process. """

    tokens: List[str]
    id: Union[Unset, str] = UNSET
    metadata: Union[TokenClassificationRecordMetadata, Unset] = UNSET
    status: Union[Unset, RecordStatus] = UNSET
    prediction: Union[TokenClassificationAnnotation, Unset] = UNSET
    annotation: Union[TokenClassificationAnnotation, Unset] = UNSET
    event_timestamp: Union[Unset, datetime.datetime] = UNSET
    raw_text: Union[Unset, Optional[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        tokens = self.tokens

        id = self.id
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        status: Union[Unset, RecordStatus] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status

        prediction: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.prediction, Unset):
            prediction = self.prediction.to_dict()

        annotation: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.annotation, Unset):
            annotation = self.annotation.to_dict()

        event_timestamp: Union[Unset, str] = UNSET
        if self.event_timestamp is not None and not isinstance(self.event_timestamp, Unset):
            event_timestamp = self.event_timestamp.isoformat()

        raw_text = self.raw_text

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {"tokens": tokens,}
        )
        if id is not UNSET:
            field_dict["id"] = id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if status is not UNSET:
            field_dict["status"] = status
        if prediction is not UNSET:
            field_dict["prediction"] = prediction
        if annotation is not UNSET:
            field_dict["annotation"] = annotation
        if event_timestamp is not UNSET:
            field_dict["event_timestamp"] = event_timestamp
        if raw_text is not UNSET:
            field_dict["raw_text"] = raw_text

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TokenClassificationRecord":
        d = src_dict.copy()
        tokens = cast(List[str], d.pop("tokens"))

        id = d.pop("id", UNSET)

        metadata: Union[TokenClassificationRecordMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if _metadata is not None and not isinstance(_metadata, Unset):
            metadata = TokenClassificationRecordMetadata.from_dict(cast(Dict[str, Any], _metadata))

        status = None
        _status = d.pop("status", UNSET)
        if _status is not None and not isinstance(_status, Unset):
            status = RecordStatus(_status)

        prediction: Union[TokenClassificationAnnotation, Unset] = UNSET
        _prediction = d.pop("prediction", UNSET)
        if _prediction is not None and not isinstance(_prediction, Unset):
            prediction = TokenClassificationAnnotation.from_dict(cast(Dict[str, Any], _prediction))

        annotation: Union[TokenClassificationAnnotation, Unset] = UNSET
        _annotation = d.pop("annotation", UNSET)
        if _annotation is not None and not isinstance(_annotation, Unset):
            annotation = TokenClassificationAnnotation.from_dict(cast(Dict[str, Any], _annotation))

        event_timestamp = None
        _event_timestamp = d.pop("event_timestamp", UNSET)
        if _event_timestamp is not None and not isinstance(_event_timestamp, Unset):
            event_timestamp = isoparse(cast(str, _event_timestamp))

        raw_text = d.pop("raw_text", UNSET)

        token_classification_record = TokenClassificationRecord(
            tokens=tokens,
            id=id,
            metadata=metadata,
            status=status,
            prediction=prediction,
            annotation=annotation,
            event_timestamp=event_timestamp,
            raw_text=raw_text,
        )

        token_classification_record.additional_properties = d
        return token_classification_record

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
