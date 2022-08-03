#  coding=utf-8
#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, root_validator, validator

from rubrix.server.apis.v0.models.commons.model import (
    BaseRecord,
    BaseSearchResults,
    ScoreRange,
)
from rubrix.server.apis.v0.models.datasets import UpdateDatasetRequest
from rubrix.server.commons.models import PredictionStatus
from rubrix.server.daos.backend.search.model import SortableField
from rubrix.server.services.search.model import (
    ServiceBaseRecordsQuery,
    ServiceBaseSearchResultsAggregations,
)
from rubrix.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationAnnotation as _TokenClassificationAnnotation,
)
from rubrix.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationDataset,
)


class TokenClassificationAnnotation(_TokenClassificationAnnotation):
    pass


class CreationTokenClassificationRecord(BaseRecord[TokenClassificationAnnotation]):

    tokens: List[str] = Field(min_items=1)
    text: str = Field()
    _raw_text: Optional[str] = Field(alias="raw_text")

    @root_validator(pre=True)
    def accept_old_fashion_text_field(cls, values):
        text, raw_text = values.get("text"), values.get("raw_text")
        text = text or raw_text
        values["text"] = cls.check_text_content(text)

        return values

    @validator("text")
    def check_text_content(cls, text: str):
        assert text and text.strip(), "No text or empty text provided"
        return text

    def extended_fields(self) -> Dict[str, Any]:
        return {
            "raw_text": self.text,  # Maintain results compatibility
        }


class TokenClassificationRecord(CreationTokenClassificationRecord):
    pass


class TokenClassificationBulkRequest(UpdateDatasetRequest):
    records: List[CreationTokenClassificationRecord]


class TokenClassificationQuery(ServiceBaseRecordsQuery):

    predicted_as: List[str] = Field(default_factory=list)
    annotated_as: List[str] = Field(default_factory=list)
    score: Optional[ScoreRange] = Field(default=None)
    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)


class TokenClassificationSearchRequest(BaseModel):
    query: TokenClassificationQuery = Field(default_factory=TokenClassificationQuery)
    sort: List[SortableField] = Field(default_factory=list)


class TokenClassificationAggregations(ServiceBaseSearchResultsAggregations):
    predicted_mentions: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    mentions: Dict[str, Dict[str, int]] = Field(default_factory=dict)


class TokenClassificationSearchResults(
    BaseSearchResults[TokenClassificationRecord, TokenClassificationAggregations]
):
    pass


class TokenClassificationDataset(ServiceTokenClassificationDataset):
    pass
