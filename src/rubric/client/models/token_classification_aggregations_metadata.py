from typing import Any, Dict

from typing import List


import attr

from ..types import UNSET, Unset

from typing import Dict
from typing import cast
from ..models.token_classification_aggregations_metadata_additional_property import (
    TokenClassificationAggregationsMetadataAdditionalProperty,
)


@attr.s(auto_attribs=True)
class TokenClassificationAggregationsMetadata:
    """  """

    additional_properties: Dict[str, TokenClassificationAggregationsMetadataAdditionalProperty] = attr.ib(
        init=False, factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @staticmethod
    def from_dict(src_dict: Dict[str, Any]) -> "TokenClassificationAggregationsMetadata":
        d = src_dict.copy()
        token_classification_aggregations_metadata = TokenClassificationAggregationsMetadata()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = TokenClassificationAggregationsMetadataAdditionalProperty.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        token_classification_aggregations_metadata.additional_properties = additional_properties
        return token_classification_aggregations_metadata

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> TokenClassificationAggregationsMetadataAdditionalProperty:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: TokenClassificationAggregationsMetadataAdditionalProperty) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
