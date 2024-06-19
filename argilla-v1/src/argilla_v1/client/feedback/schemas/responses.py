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

from argilla_v1.client.feedback.schemas.enums import ResponseStatus
from argilla_v1.client.feedback.schemas.response_values import (
    ResponseValue,
    normalize_response_value,
)
from argilla_v1.pydantic_v1 import BaseModel, Extra, validator

if TYPE_CHECKING:
    pass


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
        >>> from argilla_v1.client.feedback.schemas.responses import ResponseSchema, ValueSchema
        >>> ResponseSchema(
        ...     values={
        ...         "question_1": ValueSchema(value="answer_1"),
        ...         "question_2": ValueSchema(value="answer_2"),
        ...     }
        ... )
    """

    user_id: Optional[UUID] = None
    values: Union[List[Dict[str, ValueSchema]], Dict[str, ValueSchema], None]
    status: Union[ResponseStatus, str] = ResponseStatus.submitted

    @validator("values", always=True)
    def normalize_values(cls, values):
        if isinstance(values, list) and all(isinstance(value, dict) for value in values):
            return {k: v for value in values for k, v in value.items()}
        return values

    @validator("status")
    def normalize_status(cls, v) -> ResponseStatus:
        if isinstance(v, str):
            return ResponseStatus(v)
        return v

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

    def to_server_payload(self) -> Dict[str, Any]:
        """Method that will be used to create the payload that will be sent to Argilla
        to create a `ResponseSchema` for a `FeedbackRecord`."""
        payload = {"user_id": self.user_id, "status": self.status, **self.dict(exclude_unset=True, include={"values"})}
        return payload
