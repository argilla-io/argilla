from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Dict
from typing import cast
from ..models.record_status import RecordStatus
from typing import Union
from ..models.token_classification_query_query_metadata import TokenClassificationQueryQueryMetadata
from typing import Optional
from ..types import UNSET, Unset
from ..models.prediction_status import PredictionStatus
from typing import cast, List


@attr.s(auto_attribs=True)
class TokenClassificationQuery:
    """  """

    predicted_as: Union[Unset, List[str]] = UNSET
    annotated_as: Union[Unset, List[str]] = UNSET
    annotated_by: Union[Unset, List[str]] = UNSET
    predicted_by: Union[Unset, List[str]] = UNSET
    status: Union[Unset, List[RecordStatus]] = UNSET
    predicted: Union[Unset, PredictionStatus] = UNSET
    query_metadata: Union[Optional[TokenClassificationQueryQueryMetadata], Unset] = UNSET
    query_text: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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

        status: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.status, Unset):
            status = []
            for status_item_data in self.status:
                status_item = status_item_data.value

                status.append(status_item)

        predicted: Union[Unset, PredictionStatus] = UNSET
        if not isinstance(self.predicted, Unset):
            predicted = self.predicted

        query_metadata: Union[None, Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.query_metadata, Unset):
            query_metadata = self.query_metadata.to_dict() if self.query_metadata else None

        query_text = self.query_text

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
        if query_metadata is not UNSET:
            field_dict["query_metadata"] = query_metadata
        if query_text is not UNSET:
            field_dict["query_text"] = query_text

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TokenClassificationQuery":
        d = src_dict.copy()
        predicted_as = cast(List[str], d.pop("predicted_as", UNSET))

        annotated_as = cast(List[str], d.pop("annotated_as", UNSET))

        annotated_by = cast(List[str], d.pop("annotated_by", UNSET))

        predicted_by = cast(List[str], d.pop("predicted_by", UNSET))

        status = []
        _status = d.pop("status", UNSET)
        for status_item_data in _status or []:
            status_item = RecordStatus(status_item_data)

            status.append(status_item)

        predicted = None
        _predicted = d.pop("predicted", UNSET)
        if _predicted is not None and not isinstance((_predicted), Unset):
            predicted = PredictionStatus(_predicted)

        query_metadata = None
        _query_metadata = d.pop("query_metadata", UNSET)
        if _query_metadata is not None and not isinstance(_query_metadata, Unset):
            query_metadata = TokenClassificationQueryQueryMetadata.from_dict(cast(Dict[str, Any], _query_metadata))

        query_text = d.pop("query_text", UNSET)

        token_classification_query = TokenClassificationQuery(
            predicted_as=predicted_as,
            annotated_as=annotated_as,
            annotated_by=annotated_by,
            predicted_by=predicted_by,
            status=status,
            predicted=predicted,
            query_metadata=query_metadata,
            query_text=query_text,
        )

        token_classification_query.additional_properties = d
        return token_classification_query

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
