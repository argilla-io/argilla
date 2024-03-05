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

import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from uuid import UUID

from argilla.client.feedback.schemas.enums import QuestionTypes, ResponseStatus
from argilla.client.feedback.schemas.response_values import (
    RankingValueSchema,
    ResponseValue,
    SpanValueSchema,
    normalize_response_value,
    parse_value_response_for_question,
)
from argilla.pydantic_v1 import BaseModel, Extra, validator

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.questions import QuestionSchema
    from argilla.client.users import User


class ValueSchema(BaseModel):
    """Schema for any `FeedbackRecord` response value.

    Args:
        value: The value of the record.
    """

    value: ResponseValue

    _normalize_value = validator("value", allow_reuse=True, always=True)(normalize_response_value)


class ResponseSchema(BaseModel):
    """Schema for the `FeedbackRecord` response.

    Args:
        user_id: ID of the user that provided the response. Defaults to None, and is
            automatically fulfilled internally once the question is pushed to Argilla.
        values: Values of the response, should match the questions in the record.
        status: Status of the response. Defaults to `submitted`.

    Examples:
        >>> from argilla.client.feedback.schemas.responses import ResponseSchema, ValueSchema
        >>> ResponseSchema(
        ...     values={
        ...         "question_1": ValueSchema(value="answer_1"),
        ...         "question_2": ValueSchema(value="answer_2"),
        ...     }
        ... )
    """

    user_id: Optional[UUID] = None
    values: Union[Dict[str, ValueSchema], None]
    status: ResponseStatus = ResponseStatus.submitted

    @validator("user_id", always=True)
    def user_id_must_have_value(cls, v):
        if not v:
            warnings.warn(
                "`user_id` not provided, so it will be set to `None`. Which is not an"
                " issue, unless you're planning to log the response in Argilla, as"
                " it will be automatically set to the active `user_id`.",
            )
        return v

    class Config:
        extra = Extra.forbid
        validate_assignment = True

    def with_question_value(self, question: "QuestionSchema", value: ResponseValue) -> "ResponseSchema":
        """Returns the response value for the given record."""
        value = parse_value_response_for_question(question, value)

        values = self.values or {}
        values[question.name] = ValueSchema(value=value)

        self.values = values

        return self

    def to_server_payload(self) -> Dict[str, Any]:
        """Method that will be used to create the payload that will be sent to Argilla
        to create a `ResponseSchema` for a `FeedbackRecord`."""
        return {
            # UUID is not json serializable!!!
            "user_id": self.user_id,
            "values": {question_name: value.dict(exclude_unset=True) for question_name, value in self.values.items()}
            if self.values is not None
            else None,
            "status": self.status.value if hasattr(self.status, "value") else self.status,
        }


class ResponseBuilder:
    """Builder class to create a `ResponseSchema` instance."""

    def __init__(self):
        self._data = {}

    @classmethod
    def from_response(cls, response: ResponseSchema) -> "ResponseBuilder":
        """Method to create a `ResponseBuilder` from a `ResponseSchema` instance."""

        builder = cls()
        builder._data = response.dict(exclude_unset=True)

        return builder

    def user(self, user: "User") -> "ResponseBuilder":
        """Method to set the user that provided the response."""

        self._data["user_id"] = user.id
        return self

    def status(self, status: Union[ResponseStatus, str]) -> "ResponseBuilder":
        """Method to set the status of the response. Possible values are `submitted` or `discarded`."""

        self._data["status"] = status
        return self

    def question_value(self, question: "QuestionSchema", value: ResponseValue) -> "ResponseBuilder":
        """Method to set the value of the response for a given question. It should match the type of the question."""

        value = parse_value_response_for_question(question, value)
        values = self._data.get("values", {})

        values[question.name] = ValueSchema(value=value)
        self._data["values"] = values

        return self

    def build(self) -> ResponseSchema:
        """Method to create a `ResponseSchema` instance."""
        return ResponseSchema(**self._data)
