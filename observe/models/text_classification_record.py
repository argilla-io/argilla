from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from ..models.text_classification_record_inputs import TextClassificationRecordInputs
from typing import Union
from typing import cast
from typing import Dict
from dateutil.parser import isoparse
from ..models.text_classification_annotation import TextClassificationAnnotation
from ..models.text_classification_record_explanation import TextClassificationRecordExplanation
from ..types import UNSET, Unset
from ..models.text_classification_record_metadata import TextClassificationRecordMetadata
from ..models.record_status import RecordStatus
import datetime


@attr.s(auto_attribs=True)
class TextClassificationRecord:
    """ Data record for text classification

Attributes:
-----------
inputs: Dict[str, Any]
    textual input data from which annotation is made

prediction: TextClassificationAnnotation
    the model agent annotation

annotation: TextClassificationAnnotation
    the real annotation. This annotation should be generated
    by some human-supervised process.

multi_label: bool
    If true, all labels information are related to multilabel classification problem

explanation: Dict[str, List[TokenAttributions]]
    a dictionary map with info related to input attributions. Map is keyed by input field data,
    and should contain the tokens and its attribution for record label(s) """

    inputs: TextClassificationRecordInputs
    id: Union[Unset, str] = UNSET
    metadata: Union[TextClassificationRecordMetadata, Unset] = UNSET
    status: Union[Unset, RecordStatus] = UNSET
    prediction: Union[TextClassificationAnnotation, Unset] = UNSET
    annotation: Union[TextClassificationAnnotation, Unset] = UNSET
    event_timestamp: Union[Unset, datetime.datetime] = UNSET
    multi_label: Union[Unset, bool] = False
    explanation: Union[TextClassificationRecordExplanation, Unset] = UNSET
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
        if not isinstance(self.event_timestamp, Unset):
            event_timestamp = self.event_timestamp.isoformat()

        multi_label = self.multi_label
        explanation: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.explanation, Unset):
            explanation = self.explanation.to_dict()

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

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TextClassificationRecord":
        d = src_dict.copy()
        inputs = TextClassificationRecordInputs.from_dict(d.pop("inputs"))

        id = d.pop("id", UNSET)

        metadata: Union[TextClassificationRecordMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if _metadata is not None and not isinstance(_metadata, Unset):
            metadata = TextClassificationRecordMetadata.from_dict(cast(Dict[str, Any], _metadata))

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
        if _event_timestamp is not None:
            event_timestamp = isoparse(cast(str, _event_timestamp))

        multi_label = d.pop("multi_label", UNSET)

        explanation: Union[TextClassificationRecordExplanation, Unset] = UNSET
        _explanation = d.pop("explanation", UNSET)
        if _explanation is not None and not isinstance(_explanation, Unset):
            explanation = TextClassificationRecordExplanation.from_dict(cast(Dict[str, Any], _explanation))

        text_classification_record = TextClassificationRecord(
            inputs=inputs,
            id=id,
            metadata=metadata,
            status=status,
            prediction=prediction,
            annotation=annotation,
            event_timestamp=event_timestamp,
            multi_label=multi_label,
            explanation=explanation,
        )

        text_classification_record.additional_properties = d
        return text_classification_record

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
