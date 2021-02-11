from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Dict
import datetime
from dateutil.parser import isoparse
from ..models.text_classification_annotation import TextClassificationAnnotation
from ..models.text_classification_record_out_metadata import TextClassificationRecordOUTMetadata
from ..models.text_classification_record_out_explanation import TextClassificationRecordOUTExplanation
from typing import cast
from ..models.record_status import RecordStatus
from typing import Union
from ..types import UNSET, Unset
from ..models.prediction_status import PredictionStatus
from ..models.text_classification_record_out_inputs import TextClassificationRecordOUTInputs


@attr.s(auto_attribs=True)
class TextClassificationRecordOUT:
    """ Output record """

    inputs: TextClassificationRecordOUTInputs
    id: Union[Unset, str] = UNSET
    metadata: Union[TextClassificationRecordOUTMetadata, Unset] = UNSET
    status: Union[Unset, RecordStatus] = UNSET
    prediction: Union[TextClassificationAnnotation, Unset] = UNSET
    annotation: Union[TextClassificationAnnotation, Unset] = UNSET
    event_timestamp: Union[Unset, datetime.datetime] = UNSET
    multi_label: Union[Unset, bool] = False
    explanation: Union[TextClassificationRecordOUTExplanation, Unset] = UNSET
    last_updated: Union[Unset, datetime.datetime] = UNSET
    predicted: Union[Unset, PredictionStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        inputs = self.inputs.to_dict()

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

        multi_label = self.multi_label
        explanation: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.explanation, Unset):
            explanation = self.explanation.to_dict()

        last_updated: Union[Unset, str] = UNSET
        if self.last_updated is not None and not isinstance(self.last_updated, Unset):
            last_updated = self.last_updated.isoformat()

        predicted: Union[Unset, PredictionStatus] = UNSET
        if not isinstance(self.predicted, Unset):
            predicted = self.predicted

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {"inputs": inputs,}
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
        if multi_label is not UNSET:
            field_dict["multi_label"] = multi_label
        if explanation is not UNSET:
            field_dict["explanation"] = explanation
        if last_updated is not UNSET:
            field_dict["last_updated"] = last_updated
        if predicted is not UNSET:
            field_dict["predicted"] = predicted

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TextClassificationRecordOUT":
        d = src_dict.copy()
        inputs = TextClassificationRecordOUTInputs.from_dict(d.pop("inputs"))

        id = d.pop("id", UNSET)

        metadata: Union[TextClassificationRecordOUTMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if _metadata is not None and not isinstance(_metadata, Unset):
            metadata = TextClassificationRecordOUTMetadata.from_dict(cast(Dict[str, Any], _metadata))

        status = None
        _status = d.pop("status", UNSET)
        if _status is not None and not isinstance((_status), Unset):
            status = RecordStatus(_status)

        prediction: Union[TextClassificationAnnotation, Unset] = UNSET
        _prediction = d.pop("prediction", UNSET)
        if _prediction is not None and not isinstance(_prediction, Unset):
            prediction = TextClassificationAnnotation.from_dict(cast(Dict[str, Any], _prediction))

        annotation: Union[TextClassificationAnnotation, Unset] = UNSET
        _annotation = d.pop("annotation", UNSET)
        if _annotation is not None and not isinstance(_annotation, Unset):
            annotation = TextClassificationAnnotation.from_dict(cast(Dict[str, Any], _annotation))

        event_timestamp = None
        _event_timestamp = d.pop("event_timestamp", UNSET)
        if _event_timestamp is not None and not isinstance(_event_timestamp, Unset):
            event_timestamp = isoparse(cast(str, _event_timestamp))

        multi_label = d.pop("multi_label", UNSET)

        explanation: Union[TextClassificationRecordOUTExplanation, Unset] = UNSET
        _explanation = d.pop("explanation", UNSET)
        if _explanation is not None and not isinstance(_explanation, Unset):
            explanation = TextClassificationRecordOUTExplanation.from_dict(cast(Dict[str, Any], _explanation))

        last_updated = None
        _last_updated = d.pop("last_updated", UNSET)
        if _last_updated is not None and not isinstance(_last_updated, Unset):
            last_updated = isoparse(cast(str, _last_updated))

        predicted = None
        _predicted = d.pop("predicted", UNSET)
        if _predicted is not None and not isinstance((_predicted), Unset):
            predicted = PredictionStatus(_predicted)

        text_classification_record_out = TextClassificationRecordOUT(
            inputs=inputs,
            id=id,
            metadata=metadata,
            status=status,
            prediction=prediction,
            annotation=annotation,
            event_timestamp=event_timestamp,
            multi_label=multi_label,
            explanation=explanation,
            last_updated=last_updated,
            predicted=predicted,
        )

        text_classification_record_out.additional_properties = d
        return text_classification_record_out

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
