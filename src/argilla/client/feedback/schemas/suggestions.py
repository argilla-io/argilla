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

from typing import TYPE_CHECKING, Any, Dict, Literal, Optional
from uuid import UUID

from argilla.client.feedback.schemas.response_values import (
    ResponseValue,
    normalize_response_value,
    parse_value_response_for_question,
)
from argilla.pydantic_v1 import BaseModel, Extra, confloat, validator

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.questions import QuestionSchema


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
    value: ResponseValue
    score: Optional[confloat(ge=0, le=1)] = None
    type: Optional[Literal["model", "human"]] = None
    agent: Optional[str] = None

    _normalize_value = validator("value", allow_reuse=True, always=True)(normalize_response_value)

    class Config:
        extra = Extra.forbid
        validate_assignment = True

    def to_server_payload(self, question_name_to_id: Dict[str, UUID]) -> Dict[str, Any]:
        """Method that will be used to create the payload that will be sent to Argilla
        to create a `SuggestionSchema` for a `FeedbackRecord`."""
        payload = self.dict(exclude_unset=True, include={"type", "score", "value", "agent"})
        payload["question_id"] = str(question_name_to_id[self.question_name])

        return payload
