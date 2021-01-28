from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from ..models.token_classification_aggregations_words import TokenClassificationAggregationsWords
from ..models.token_classification_aggregations_status import TokenClassificationAggregationsStatus
from ..models.token_classification_aggregations_predicted_as import TokenClassificationAggregationsPredictedAs
from ..types import UNSET, Unset
from ..models.token_classification_aggregations_predicted_by import TokenClassificationAggregationsPredictedBy
from typing import cast
from ..models.token_classification_aggregations_annotated_as import TokenClassificationAggregationsAnnotatedAs
from ..models.token_classification_aggregations_annotated_by import TokenClassificationAggregationsAnnotatedBy
from ..models.token_classification_aggregations_predicted import TokenClassificationAggregationsPredicted
from ..models.token_classification_aggregations_metadata import TokenClassificationAggregationsMetadata
from typing import Dict
from typing import Union


@attr.s(auto_attribs=True)
class TokenClassificationAggregations:
    """  """

    predicted_as: Union[TokenClassificationAggregationsPredictedAs, Unset] = UNSET
    annotated_as: Union[TokenClassificationAggregationsAnnotatedAs, Unset] = UNSET
    annotated_by: Union[TokenClassificationAggregationsAnnotatedBy, Unset] = UNSET
    predicted_by: Union[TokenClassificationAggregationsPredictedBy, Unset] = UNSET
    status: Union[TokenClassificationAggregationsStatus, Unset] = UNSET
    predicted: Union[TokenClassificationAggregationsPredicted, Unset] = UNSET
    metadata: Union[TokenClassificationAggregationsMetadata, Unset] = UNSET
    words: Union[TokenClassificationAggregationsWords, Unset] = UNSET
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

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TokenClassificationAggregations":
        d = src_dict.copy()
        predicted_as: Union[TokenClassificationAggregationsPredictedAs, Unset] = UNSET
        _predicted_as = d.pop("predicted_as", UNSET)
        if _predicted_as is not None and not isinstance(_predicted_as, Unset):
            predicted_as = TokenClassificationAggregationsPredictedAs.from_dict(cast(Dict[str, Any], _predicted_as))

        annotated_as: Union[TokenClassificationAggregationsAnnotatedAs, Unset] = UNSET
        _annotated_as = d.pop("annotated_as", UNSET)
        if _annotated_as is not None and not isinstance(_annotated_as, Unset):
            annotated_as = TokenClassificationAggregationsAnnotatedAs.from_dict(cast(Dict[str, Any], _annotated_as))

        annotated_by: Union[TokenClassificationAggregationsAnnotatedBy, Unset] = UNSET
        _annotated_by = d.pop("annotated_by", UNSET)
        if _annotated_by is not None and not isinstance(_annotated_by, Unset):
            annotated_by = TokenClassificationAggregationsAnnotatedBy.from_dict(cast(Dict[str, Any], _annotated_by))

        predicted_by: Union[TokenClassificationAggregationsPredictedBy, Unset] = UNSET
        _predicted_by = d.pop("predicted_by", UNSET)
        if _predicted_by is not None and not isinstance(_predicted_by, Unset):
            predicted_by = TokenClassificationAggregationsPredictedBy.from_dict(cast(Dict[str, Any], _predicted_by))

        status: Union[TokenClassificationAggregationsStatus, Unset] = UNSET
        _status = d.pop("status", UNSET)
        if _status is not None and not isinstance(_status, Unset):
            status = TokenClassificationAggregationsStatus.from_dict(cast(Dict[str, Any], _status))

        predicted: Union[TokenClassificationAggregationsPredicted, Unset] = UNSET
        _predicted = d.pop("predicted", UNSET)
        if _predicted is not None and not isinstance(_predicted, Unset):
            predicted = TokenClassificationAggregationsPredicted.from_dict(cast(Dict[str, Any], _predicted))

        metadata: Union[TokenClassificationAggregationsMetadata, Unset] = UNSET
        _metadata = d.pop("metadata", UNSET)
        if _metadata is not None and not isinstance(_metadata, Unset):
            metadata = TokenClassificationAggregationsMetadata.from_dict(cast(Dict[str, Any], _metadata))

        words: Union[TokenClassificationAggregationsWords, Unset] = UNSET
        _words = d.pop("words", UNSET)
        if _words is not None and not isinstance(_words, Unset):
            words = TokenClassificationAggregationsWords.from_dict(cast(Dict[str, Any], _words))

        token_classification_aggregations = TokenClassificationAggregations(
            predicted_as=predicted_as,
            annotated_as=annotated_as,
            annotated_by=annotated_by,
            predicted_by=predicted_by,
            status=status,
            predicted=predicted,
            metadata=metadata,
            words=words,
        )

        token_classification_aggregations.additional_properties = d
        return token_classification_aggregations

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
