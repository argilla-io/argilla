from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import Union
from typing import Optional
from ..models.record_status import RecordStatus
from ..models.token_classification_record_out_metadata import TokenClassificationRecordOUTMetadata
from ..models.token_classification_annotation import TokenClassificationAnnotation
import datetime
from typing import Dict
from ..models.prediction_status import PredictionStatus
from typing import cast, List
from typing import cast


@attr.s(auto_attribs=True)
class TokenClassificationRecordOUT:
    """ Record output  """

    tokens: List[str]
    id: Union[Unset, str] = UNSET
    metadata: Union[TokenClassificationRecordOUTMetadata, Unset] = UNSET
    status: Union[Unset, RecordStatus] = UNSET
    prediction: Union[TokenClassificationAnnotation, Unset] = UNSET
    annotation: Union[TokenClassificationAnnotation, Unset] = UNSET
    raw_text: Union[Unset, Optional[str]] = UNSET
    last_updated: Union[Unset, datetime.datetime] = UNSET
    predicted: Union[Unset, PredictionStatus] = UNSET
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

        raw_text = self.raw_text
        last_updated: Union[Unset, str] = UNSET
        if not isinstance(self.last_updated, Unset):
            last_updated = self.last_updated.isoformat()

        predicted: Union[Unset, PredictionStatus] = UNSET
        if not isinstance(self.predicted, Unset):
            predicted = self.predicted

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
        if raw_text is not UNSET:
            field_dict["raw_text"] = raw_text
        if last_updated is not UNSET:
            field_dict["last_updated"] = last_updated
        if predicted is not UNSET:
            field_dict["predicted"] = predicted

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TokenClassificationRecordOUT":
        d = src_dict.copy()
        tokens = cast(List[str], d.pop("tokens"))

        id = d.pop("id", UNSET)

        metadata: Union[TokenClassificationRecordOUTMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if _metadata is not None and not isinstance(_metadata, Unset):
            metadata = TokenClassificationRecordOUTMetadata.from_dict(cast(Dict[str, Any], _metadata))

        status = None
        _status = d.pop("status", UNSET)
        if _status is not None and not isinstance((_status), Unset):
            status = RecordStatus(_status)

        prediction: Union[TokenClassificationAnnotation, Unset] = UNSET
        _prediction = d.pop("prediction", UNSET)
        if _prediction is not None and not isinstance(_prediction, Unset):
            prediction = TokenClassificationAnnotation.from_dict(cast(Dict[str, Any], _prediction))

        annotation: Union[TokenClassificationAnnotation, Unset] = UNSET
        _annotation = d.pop("annotation", UNSET)
        if _annotation is not None and not isinstance(_annotation, Unset):
            annotation = TokenClassificationAnnotation.from_dict(cast(Dict[str, Any], _annotation))

        raw_text = d.pop("raw_text", UNSET)

        last_updated = None
        _last_updated = d.pop("last_updated", UNSET)
        if _last_updated is not None:
            last_updated = isoparse(cast(str, _last_updated))

        predicted = None
        _predicted = d.pop("predicted", UNSET)
        if _predicted is not None and not isinstance((_predicted), Unset):
            predicted = PredictionStatus(_predicted)

        token_classification_record_out = TokenClassificationRecordOUT(
            tokens=tokens,
            id=id,
            metadata=metadata,
            status=status,
            prediction=prediction,
            annotation=annotation,
            raw_text=raw_text,
            last_updated=last_updated,
            predicted=predicted,
        )

        token_classification_record_out.additional_properties = d
        return token_classification_record_out

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
