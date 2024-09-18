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

from uuid import UUID
from datetime import datetime
from typing import Any, List, Literal, Optional, Union
from typing_extensions import Annotated

from argilla_server.api.schemas.v1.questions import QuestionName
from argilla_server.api.schemas.v1.responses import (
    MultiLabelSelectionQuestionResponseValue,
    RankingQuestionResponseValue,
    RatingQuestionResponseValue,
    SpanQuestionResponseValue,
    TextAndLabelSelectionQuestionResponseValue,
)
from argilla_server.enums import SuggestionType

# from argilla_server.pydantic_v1 import BaseModel, Field
from pydantic import ConfigDict, BaseModel, Field

# Pydantic v2 error: look-around, including look-ahead and look-behind, is not supported so rewriting it:
# AGENT_REGEX = r"^(?=.*[a-zA-Z0-9])[a-zA-Z0-9-_:\.\/\s]+$"
AGENT_REGEX = r"^[a-zA-Z0-9-_:\.\/\s]*[a-zA-Z0-9][a-zA-Z0-9-_:\.\/\s]*$"
AGENT_MIN_LENGTH = 1
AGENT_MAX_LENGTH = 200

SCORE_MIN_ITEMS = 1
SCORE_GREATER_THAN_OR_EQUAL = 0
SCORE_LESS_THAN_OR_EQUAL = 1


class SuggestionFilterScope(BaseModel):
    entity: Literal["suggestion"]
    question: QuestionName
    property: Optional[Union[Literal["value"], Literal["agent"], Literal["score"]]] = "value"


class SearchSuggestionOptionsQuestion(BaseModel):
    id: UUID
    name: str


class SearchSuggestionOptions(BaseModel):
    question: SearchSuggestionOptionsQuestion
    agents: List[str]


class SearchSuggestionsOptions(BaseModel):
    items: List[SearchSuggestionOptions]


class BaseSuggestion(BaseModel):
    question_id: UUID
    type: Optional[SuggestionType] = None
    value: Any
    agent: Optional[str] = None
    score: Optional[Union[float, List[float]]] = None


class Suggestion(BaseSuggestion):
    id: UUID
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Suggestions(BaseModel):
    items: List[Suggestion]


SuggestionScore = Annotated[
    float,
    Field(..., ge=SCORE_GREATER_THAN_OR_EQUAL, le=SCORE_LESS_THAN_OR_EQUAL),
]

SuggestionScores = Annotated[
    SuggestionScore,
    Field(..., min_length=SCORE_MIN_ITEMS),
]


class SuggestionCreate(BaseSuggestion):
    value: Union[
        SpanQuestionResponseValue,
        RankingQuestionResponseValue,
        MultiLabelSelectionQuestionResponseValue,
        RatingQuestionResponseValue,
        TextAndLabelSelectionQuestionResponseValue,
    ]
    agent: Optional[str] = Field(
        None,
        pattern=AGENT_REGEX,
        min_length=AGENT_MIN_LENGTH,
        max_length=AGENT_MAX_LENGTH,
        description="Agent used to generate the suggestion",
    )
    # score: Optional[Union[float, List[float]]] = Field(
    #     None,
    #     min_length=SCORE_MIN_ITEMS,
    #     ge=SCORE_GREATER_THAN_OR_EQUAL,
    #     le=SCORE_LESS_THAN_OR_EQUAL,
    #     description="The score assigned to the suggestion",
    # )
    score: Optional[Union[SuggestionScore, SuggestionScores]] = Field(
        None, description="The score assigned to the suggestion"
    )
