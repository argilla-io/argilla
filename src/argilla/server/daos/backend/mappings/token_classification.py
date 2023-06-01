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

from typing import Optional

from pydantic import BaseModel, Field

from argilla.server.daos.backend.mappings.helpers import mappings
from argilla.server.daos.backend.query_helpers import nested_mappings_from_base_model


class MentionMetrics(BaseModel):
    """Mention metrics model"""

    value: str
    label: str
    score: float = Field(ge=0.0)
    capitalness: Optional[str] = Field(None)


class TokenMetrics(BaseModel):
    value: str
    capitalness: Optional[str] = None


def token_classification_mappings():
    metrics_mentions_mappings = nested_mappings_from_base_model(MentionMetrics)
    return {
        "_source": mappings.source(
            excludes=[
                "predicted",
                "predicted_as",
                "predicted_by",
                "annotated_as",
                "annotated_by",
                "score",
                "predicted_mentions",
                "mentions",
            ]
        ),
        "properties": {
            "predicted": mappings.keyword_field(),
            "annotated_as": mappings.keyword_field(enable_text_search=True),
            "predicted_as": mappings.keyword_field(enable_text_search=True),
            "score": {"type": "float"},
            "tokens": mappings.keyword_field(),
            "metrics.tokens": nested_mappings_from_base_model(TokenMetrics),
            "metrics.predicted.mentions": metrics_mentions_mappings,
            "metrics.annotated.mentions": metrics_mentions_mappings,
        },
    }
