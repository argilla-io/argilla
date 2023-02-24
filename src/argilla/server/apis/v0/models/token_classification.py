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
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, root_validator, validator

from argilla.server.apis.v0.models.commons.model import (
    BaseRecord,
    BaseRecordInputs,
    BaseSearchResults,
    ScoreRange,
)
from argilla.server.commons.models import PredictionStatus
from argilla.server.daos.backend.search.model import SortableField
from argilla.server.schemas.datasets import UpdateDatasetRequest
from argilla.server.services.search.model import (
    ServiceBaseRecordsQuery,
    ServiceBaseSearchResultsAggregations,
)
from argilla.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationAnnotation as _TokenClassificationAnnotation,
)


class TokenClassificationAnnotation(_TokenClassificationAnnotation):
    pass


class TokenClassificationRecordInputs(BaseRecordInputs[TokenClassificationAnnotation]):
    text: str = Field()
    tokens: List[str] = Field(min_items=1)
    # TODO(@frascuchon): Delete this field and all related logic
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


class TokenClassificationRecord(TokenClassificationRecordInputs, BaseRecord[TokenClassificationAnnotation]):
    pass


class TokenClassificationBulkRequest(UpdateDatasetRequest):
    records: List[TokenClassificationRecordInputs]


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


class TokenClassificationSearchResults(BaseSearchResults[TokenClassificationRecord, TokenClassificationAggregations]):
    pass
