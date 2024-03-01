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

from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from argilla.pydantic_v1 import BaseModel, Extra, StrictInt, StrictStr, confloat, conint, constr, root_validator


class RankingValueSchema(BaseModel):
    """Schema for the `RankingQuestion` response value for a `RankingQuestion`. Note that
    we may have more than one record in the same rank.

    Args:
        value: The value of the record.
        rank: The rank of the record.
    """

    value: StrictStr
    rank: Optional[conint(ge=1)] = None


class SpanSuggestion(BaseModel):
    """Schema for the `SpanQuestion` response value for a `SpanQuestion`.

    Args:
        value: The label value of the span.
        start: The start of the span.
        end: The end of the span.
        score: The score of the span.
    """

    value: constr(min_length=1)
    start: conint(ge=0)
    end: conint(ge=0)
    score: Optional[confloat(ge=0.0, le=1.0)] = None

    @root_validator
    def check_span(cls, values):
        if values["start"] > values["end"]:
            raise ValueError("The start of the span must be less than the end.")
        return values


SuggestionValue = Union[
    StrictStr,
    StrictInt,
    List[str],
    List[RankingValueSchema],
    List[SpanSuggestion],
]


class SuggestionSchema(BaseModel):
    """Schema for the suggestions for the questions related to the record.

    Args:
        question_name: name of the question in the `FeedbackDataset`.
        type: type of the question. Defaults to None. Possible values are `model` or `human`.
        score: score of the suggestion. Defaults to None.
        value: value of the suggestion, which should match the type of the question.
        agent: agent that generated the suggestion. Defaults to None.

    Examples:
        >>> from argilla.client.feedback.schemas.suggestions import SuggestionSchema
        >>> SuggestionSchema(
        ...     question_name="question-1",
        ...     type="model",
        ...     score=0.9,
        ...     value="This is the first suggestion",
        ...     agent="agent-1",
        ... )
    """

    question_name: str
    type: Optional[Literal["model", "human"]] = None
    score: Optional[confloat(ge=0, le=1)] = None
    value: SuggestionValue
    agent: Optional[str] = None

    class Config:
        extra = Extra.forbid
        validate_assignment = True

    def to_server_payload(self, question_name_to_id: Dict[str, UUID]) -> Dict[str, Any]:
        """Method that will be used to create the payload that will be sent to Argilla
        to create a `SuggestionSchema` for a `FeedbackRecord`."""
        payload = self.dict(exclude_none=True, include={"type", "score", "value", "agent"})
        payload["question_id"] = str(question_name_to_id[self.question_name])

        return payload
