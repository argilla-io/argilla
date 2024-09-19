# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import warnings
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Union
from uuid import UUID

from argilla._exceptions._responses import RecordResponsesError
from argilla._models import ResponseStatus as ResponseStatusModel
from argilla._models import UserResponseModel
from argilla._resource import Resource
from argilla.settings import RankingQuestion

if TYPE_CHECKING:
    from argilla import Argilla, Dataset, Record

__all__ = ["Response", "UserResponse", "ResponseStatus"]


class ResponseStatus(str, Enum):
    """Enum for the status of a response"""

    draft = "draft"
    submitted = "submitted"
    discarded = "discarded"


class Response:
    """Class for interacting with Argilla Responses of records. Responses are answers to questions by a user.
    Therefore, a record question can have multiple responses, one for each user that has answered the question.
    A `Response` is typically created by a user in the UI or consumed from a data source as a label,
    unlike a `Suggestion` which is typically created by a model prediction.

    """

    def __init__(
        self,
        question_name: str,
        value: Any,
        user_id: UUID,
        status: Optional[Union[ResponseStatus, str]] = None,
        _record: Optional["Record"] = None,
    ) -> None:
        """Initializes a `Response` for a `Record` with a user_id and value

        Attributes:
            question_name (str): The name of the question that the suggestion is for.
            value (str): The value of the response
            user_id (UUID): The id of the user that submits the response
            status (Union[ResponseStatus, str]): The status of the response as "draft", "submitted", "discarded".
        """

        if question_name is None:
            raise ValueError("question_name is required")
        if value is None:
            raise ValueError("value is required")
        if user_id is None:
            raise ValueError("user_id is required")

        if isinstance(status, str):
            status = ResponseStatus(status)

        self.record = _record
        self.question_name = question_name
        self.value = value
        self.user_id = user_id
        self.status = status

    def serialize(self) -> dict[str, Any]:
        """Serializes the Response to a dictionary. This is principally used for sending the response to the API, \
            but can be used for data wrangling or manual export.

        Returns:
            dict[str, Any]: The serialized response as a dictionary with keys `question_name`, `value`, and `user_id`.

        Examples:

        ```python
        response = rg.Response("label", "negative", user_id=user.id)
        response.serialize()
        ```
        """
        return {
            "question_name": self.question_name,
            "value": self.value,
            "user_id": self.user_id,
            "status": self.status,
        }

    #####################
    # Private Interface #
    #####################


class UserResponse(Resource):
    """
    Class for interacting with Argilla User Responses of records.  The UserResponse class is a collection
    of responses to questions for a given user. UserResponses are typically created by a user in the UI and
    are defined by ingesting a list of responses from a third-party data source.

    In most cases users will interact with the `UserResponse` class through the `Record` class when
    collected from the server or when creating new records.

    Attributes:
        responses (List[Response]): A list of responses to questions for the user

    """

    responses: List[Response]

    _model: UserResponseModel

    def __init__(
        self,
        responses: List[Response],
        client: Optional["Argilla"] = None,
        _record: Optional["Record"] = None,
    ) -> None:
        """Initializes a UserResponse with a user and a set of question answers"""

        super().__init__(client=client)

        self._record = _record
        self._model = UserResponseModel(
            values=self.__responses_as_model_values(responses),
            status=self._compute_status_from_responses(responses),
            user_id=self._compute_user_id_from_responses(responses),
        )

    def __iter__(self) -> Iterable[Response]:
        return iter(self.responses)

    @property
    def status(self) -> ResponseStatus:
        """Returns the status of the UserResponse"""
        return self._model.status

    @status.setter
    def status(self, status: ResponseStatus) -> None:
        """Sets the status of the UserResponse"""
        self._model.status = status

    @property
    def user_id(self) -> UUID:
        """Returns the user_id of the UserResponse"""
        return self._model.user_id

    @user_id.setter
    def user_id(self, user_id: UUID) -> None:
        """Sets the user_id of the UserResponse"""
        self._model.user_id = user_id

    @property
    def responses(self) -> List[Response]:
        """Returns the list of responses"""
        return self.__model_as_responses_list(self._model)

    @property
    def record(self) -> "Record":
        """Returns the record associated with the UserResponse"""
        return self._record

    @record.setter
    def record(self, record: "Record") -> None:
        """Sets the record associated with the UserResponse"""
        self._record = record

    @classmethod
    def from_model(cls, model: UserResponseModel, dataset: "Dataset") -> "UserResponse":
        """Creates a UserResponse from a ResponseModel"""
        responses = cls.__model_as_responses_list(model)
        for response in responses:
            question = dataset.settings.questions[response.question_name]
            # We need to adapt the ranking question value to the expected format
            if isinstance(question, RankingQuestion):
                response.value = cls.__ranking_from_model_value(response.value)  # type: ignore

        return cls(responses=responses)

    def api_model(self):
        """Returns the model that is used to interact with the API"""

        values = self.__responses_as_model_values(self.responses)
        for question_name, value in values.items():
            question = self._record.dataset.settings.questions[question_name]
            if question is None:
                raise RecordResponsesError(
                    f"Record response is invalid because question with name={question_name} does not exist in the dataset ({self._record.dataset.name}). Available questions are: {list(self._record.dataset.settings.questions._properties_by_name.keys())}"
                )
            if isinstance(question, RankingQuestion):
                value["value"] = self.__ranking_to_model_value(value["value"])

        return UserResponseModel(values=values, status=self._model.status, user_id=self._model.user_id)

    def to_dict(self) -> Dict[str, Any]:
        """Returns the UserResponse as a dictionary"""
        return self._model.model_dump()

    @staticmethod
    def _compute_status_from_responses(responses: List[Response]) -> ResponseStatus:
        """Computes the status of the UserResponse from the responses"""
        statuses = set([answer.status for answer in responses if answer.status is not None])
        if len(statuses) > 1:
            warnings.warn(f"Multiple status found in user responses. Using {ResponseStatus.draft.value!r} as default.")
        elif len(statuses) == 1:
            return ResponseStatusModel(next(iter(statuses)))
        return ResponseStatusModel.draft

    @staticmethod
    def _compute_user_id_from_responses(responses: List[Response]) -> Optional[UUID]:
        if len(responses) == 0:
            return None

        user_ids = set([answer.user_id for answer in responses])
        if len(user_ids) > 1:
            raise ValueError("Multiple user_ids found in user responses.")
        return next(iter(user_ids))

    @staticmethod
    def __responses_as_model_values(responses: List[Response]) -> Dict[str, Dict[str, Any]]:
        """Creates a dictionary of response values from a list of Responses"""
        return {answer.question_name: {"value": answer.value} for answer in responses}

    @classmethod
    def __model_as_responses_list(cls, model: UserResponseModel) -> List[Response]:
        """Creates a list of Responses from a UserResponseModel without changing the format of the values"""

        return [
            Response(
                question_name=question_name,
                value=value["value"],
                user_id=model.user_id,
                status=model.status,
            )
            for question_name, value in model.values.items()
        ]

    @classmethod
    def __ranking_from_model_value(cls, value: List[Dict[str, Any]]) -> List[str]:
        return [v["value"] for v in value]

    @classmethod
    def __ranking_to_model_value(cls, value: List[str]) -> List[Dict[str, str]]:
        return [{"value": v} for v in value]
