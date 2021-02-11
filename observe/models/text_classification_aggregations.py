from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from ..models.text_classification_aggregations_annotated_by import TextClassificationAggregationsAnnotatedBy
from ..models.text_classification_aggregations_metadata import TextClassificationAggregationsMetadata
from typing import Dict
from ..models.text_classification_aggregations_predicted_by import TextClassificationAggregationsPredictedBy
from ..models.text_classification_aggregations_words import TextClassificationAggregationsWords
from ..models.text_classification_aggregations_inputs import TextClassificationAggregationsInputs
from ..models.text_classification_aggregations_status import TextClassificationAggregationsStatus
from typing import cast
from ..models.text_classification_aggregations_annotated_as import TextClassificationAggregationsAnnotatedAs
from typing import Union
from ..models.text_classification_aggregations_predicted import TextClassificationAggregationsPredicted
from ..types import UNSET, Unset
from ..models.text_classification_aggregations_confidence import TextClassificationAggregationsConfidence
from ..models.text_classification_aggregations_predicted_as import TextClassificationAggregationsPredictedAs


@attr.s(auto_attribs=True)
class TextClassificationAggregations:
    """  """

    predicted_as: Union[TextClassificationAggregationsPredictedAs, Unset] = UNSET
    annotated_as: Union[TextClassificationAggregationsAnnotatedAs, Unset] = UNSET
    annotated_by: Union[TextClassificationAggregationsAnnotatedBy, Unset] = UNSET
    predicted_by: Union[TextClassificationAggregationsPredictedBy, Unset] = UNSET
    status: Union[TextClassificationAggregationsStatus, Unset] = UNSET
    predicted: Union[TextClassificationAggregationsPredicted, Unset] = UNSET
    metadata: Union[TextClassificationAggregationsMetadata, Unset] = UNSET
    words: Union[TextClassificationAggregationsWords, Unset] = UNSET
    confidence: Union[TextClassificationAggregationsConfidence, Unset] = UNSET
    inputs: Union[TextClassificationAggregationsInputs, Unset] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        predicted_as: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.predicted_as, Unset):
            predicted_as = self.predicted_as.to_dict()

        annotated_as: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.annotated_as, Unset):
            annotated_as = self.annotated_as.to_dict()

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

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        words: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.words, Unset):
            words = self.words.to_dict()

        confidence: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.confidence, Unset):
            confidence = self.confidence.to_dict()

        inputs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.inputs, Unset):
            inputs = self.inputs.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if predicted_as is not UNSET:
            field_dict["predicted_as"] = predicted_as
        if annotated_as is not UNSET:
            field_dict["annotated_as"] = annotated_as
        if annotated_by is not UNSET:
            field_dict["annotated_by"] = annotated_by
        if predicted_by is not UNSET:
            field_dict["predicted_by"] = predicted_by
        if status is not UNSET:
            field_dict["status"] = status
        if predicted is not UNSET:
            field_dict["predicted"] = predicted
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if words is not UNSET:
            field_dict["words"] = words
        if confidence is not UNSET:
            field_dict["confidence"] = confidence
        if inputs is not UNSET:
            field_dict["inputs"] = inputs

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TextClassificationAggregations":
        d = src_dict.copy()
        predicted_as: Union[TextClassificationAggregationsPredictedAs, Unset] = UNSET
        _predicted_as = d.pop("predicted_as", UNSET)
        if _predicted_as is not None and not isinstance(_predicted_as, Unset):
            predicted_as = TextClassificationAggregationsPredictedAs.from_dict(cast(Dict[str, Any], _predicted_as))

        annotated_as: Union[TextClassificationAggregationsAnnotatedAs, Unset] = UNSET
        _annotated_as = d.pop("annotated_as", UNSET)
        if _annotated_as is not None and not isinstance(_annotated_as, Unset):
            annotated_as = TextClassificationAggregationsAnnotatedAs.from_dict(cast(Dict[str, Any], _annotated_as))

        annotated_by: Union[TextClassificationAggregationsAnnotatedBy, Unset] = UNSET
        _annotated_by = d.pop("annotated_by", UNSET)
        if _annotated_by is not None and not isinstance(_annotated_by, Unset):
            annotated_by = TextClassificationAggregationsAnnotatedBy.from_dict(cast(Dict[str, Any], _annotated_by))

        predicted_by: Union[TextClassificationAggregationsPredictedBy, Unset] = UNSET
        _predicted_by = d.pop("predicted_by", UNSET)
        if _predicted_by is not None and not isinstance(_predicted_by, Unset):
            predicted_by = TextClassificationAggregationsPredictedBy.from_dict(cast(Dict[str, Any], _predicted_by))

        status: Union[TextClassificationAggregationsStatus, Unset] = UNSET
        _status = d.pop("status", UNSET)
        if _status is not None and not isinstance(_status, Unset):
            status = TextClassificationAggregationsStatus.from_dict(cast(Dict[str, Any], _status))

        predicted: Union[TextClassificationAggregationsPredicted, Unset] = UNSET
        _predicted = d.pop("predicted", UNSET)
        if _predicted is not None and not isinstance(_predicted, Unset):
            predicted = TextClassificationAggregationsPredicted.from_dict(cast(Dict[str, Any], _predicted))

        metadata: Union[TextClassificationAggregationsMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if _metadata is not None and not isinstance(_metadata, Unset):
            metadata = TextClassificationAggregationsMetadata.from_dict(cast(Dict[str, Any], _metadata))

        words: Union[TextClassificationAggregationsWords, Unset] = UNSET
        _words = d.pop("words", UNSET)
        if _words is not None and not isinstance(_words, Unset):
            words = TextClassificationAggregationsWords.from_dict(cast(Dict[str, Any], _words))

        confidence: Union[TextClassificationAggregationsConfidence, Unset] = UNSET
        _confidence = d.pop("confidence", UNSET)
        if _confidence is not None and not isinstance(_confidence, Unset):
            confidence = TextClassificationAggregationsConfidence.from_dict(cast(Dict[str, Any], _confidence))

        inputs: Union[TextClassificationAggregationsInputs, Unset] = UNSET
        _inputs = d.pop("inputs", UNSET)
        if _inputs is not None and not isinstance(_inputs, Unset):
            inputs = TextClassificationAggregationsInputs.from_dict(cast(Dict[str, Any], _inputs))

        text_classification_aggregations = TextClassificationAggregations(
            predicted_as=predicted_as,
            annotated_as=annotated_as,
            annotated_by=annotated_by,
            predicted_by=predicted_by,
            status=status,
            predicted=predicted,
            metadata=metadata,
            words=words,
            confidence=confidence,
            inputs=inputs,
        )

        text_classification_aggregations.additional_properties = d
        return text_classification_aggregations

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
