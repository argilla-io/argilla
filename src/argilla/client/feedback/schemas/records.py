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
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Tuple, Union
from uuid import UUID

from argilla.client.feedback.schemas.enums import RecordSortField, ResponseStatus, SortOrder
from argilla.pydantic_v1 import BaseModel, Extra, Field, PrivateAttr, StrictInt, StrictStr, conint, validator

if TYPE_CHECKING:
    from argilla.client.feedback.unification import UnifiedValueSchema


class RankingValueSchema(BaseModel):
    """Schema for the `RankingQuestion` response value for a `RankingQuestion`. Note that
    we may have more than one record in the same rank.

    Args:
        value: The value of the record.
        rank: The rank of the record.
    """

    value: StrictStr
    rank: Optional[conint(ge=1)] = None


class ValueSchema(BaseModel):
    """Schema for any `FeedbackRecord` response value.

    Args:
        value: The value of the record.
    """

    value: Union[StrictStr, StrictInt, List[str], List[RankingValueSchema]]


class ResponseSchema(BaseModel):
    """Schema for the `FeedbackRecord` response.

    Args:
        user_id: ID of the user that provided the response. Defaults to None, and is
            automatically fulfilled internally once the question is pushed to Argilla.
        values: Values of the response, should match the questions in the record.
        status: Status of the response. Defaults to `submitted`.

    Examples:
        >>> from argilla.client.feedback.schemas.records import ResponseSchema
        >>> ResponseSchema(
        ...     values={
        ...         "question_1": {"value": "answer_1"},
        ...         "question_2": {"value": "answer_2"},
        ...     }
        ... )
    """

    user_id: Optional[UUID] = None
    values: Union[Dict[str, ValueSchema], None]
    status: ResponseStatus = ResponseStatus.submitted

    class Config:
        extra = Extra.forbid
        validate_assignment = True

    @validator("user_id", always=True)
    def user_id_must_have_value(cls, v):
        if not v:
            warnings.warn(
                "`user_id` not provided, so it will be set to `None`. Which is not an"
                " issue, unless you're planning to log the response in Argilla, as"
                " it will be automatically set to the active `user_id`.",
            )
        return v

    def to_server_payload(self) -> Dict[str, Any]:
        """Method that will be used to create the payload that will be sent to Argilla
        to create a `ResponseSchema` for a `FeedbackRecord`."""
        return {
            # UUID is not json serializable!!!
            "user_id": self.user_id,
            "values": {question_name: value.dict() for question_name, value in self.values.items()}
            if self.values is not None
            else None,
            "status": self.status.value if hasattr(self.status, "value") else self.status,
        }


class SuggestionSchema(BaseModel):
    """Schema for the suggestions for the questions related to the record.

    Args:
        question_name: name of the question in the `FeedbackDataset`.
        type: type of the question. Defaults to None. Possible values are `model` or `human`.
        score: score of the suggestion. Defaults to None.
        value: value of the suggestion, which should match the type of the question.
        agent: agent that generated the suggestion. Defaults to None.

    Examples:
        >>> from argilla.client.feedback.schemas.records import SuggestionSchema
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
    score: Optional[float] = None
    value: Any
    agent: Optional[str] = None

    class Config:
        extra = Extra.forbid
        validate_assignment = True

    def to_server_payload(self, question_name_to_id: Dict[str, UUID]) -> Dict[str, Any]:
        """Method that will be used to create the payload that will be sent to Argilla
        to create a `SuggestionSchema` for a `FeedbackRecord`."""
        payload = {}
        payload["question_id"] = str(question_name_to_id[self.question_name])
        payload["value"] = self.value
        if self.type:
            payload["type"] = self.type
        if self.score:
            payload["score"] = self.score
        if self.agent:
            payload["agent"] = self.agent
        return payload


class FeedbackRecord(BaseModel):
    """Schema for the records of a `FeedbackDataset`.

    Args:
        fields: Fields that match the `FeedbackDataset` defined fields. So this attribute
            contains the actual information shown in the UI for each record, being the
            record itself.
        metadata: Metadata to be included to enrich the information for a given record.
            Note that the metadata is not shown in the UI so you'll just be able to see
            that programmatically after pulling the records. Defaults to None.
        responses: Responses given by either the current user, or one or a collection of
            users that must exist in Argilla. Each response corresponds to one of the
            `FeedbackDataset` questions, so the values should match the question type.
            Defaults to None.
        suggestions: A list of `SuggestionSchema` that contains the suggestions
            for the current record. Every suggestion is linked to only one
            question. Defaults to an empty list.
        external_id: The external ID of the record, which means that the user can
            specify this ID to identify the record no matter what the Argilla ID is.
            Defaults to None.

    Examples:
        >>> from argilla.client.feedback.schemas.records import FeedbackRecord, ResponseSchema, SuggestionSchema, ValueSchema
        >>> FeedbackRecord(
        ...     fields={"text": "This is the first record", "label": "positive"},
        ...     metadata={"first": True, "nested": {"more": "stuff"}},
        ...     responses=[ # optional
        ...         ResponseSchema(
        ...             user_id="user-1",
        ...             values={
        ...                 "question-1": ValueSchema(value="This is the first answer"),
        ...                 "question-2": ValueSchema(value=5),
        ...             },
        ...             status="submitted",
        ...         ),
        ...     ],
        ...     suggestions=[ # optional
        ...         SuggestionSchema(
        ...            question_name="question-1",
        ...            type="model",
        ...            score=0.9,
        ...            value="This is the first suggestion",
        ...            agent="agent-1",
        ...         ),
        ...     external_id="entry-1",
        ... )

    """

    fields: Dict[str, Union[str, None]]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    vectors: Dict[str, List[float]] = Field(default_factory=dict)
    responses: List[ResponseSchema] = Field(default_factory=list)
    suggestions: Union[Tuple[SuggestionSchema], List[SuggestionSchema]] = Field(default_factory=tuple)
    external_id: Optional[str] = None

    _unified_responses: Optional[Dict[str, List["UnifiedValueSchema"]]] = PrivateAttr(default_factory=dict)

    class Config:
        extra = Extra.forbid
        validate_assignment = True

    @validator("suggestions", always=True)
    def normalize_suggestions(cls, values: Any) -> Tuple:
        if not isinstance(values, tuple):
            return tuple([v for v in values])
        return values

    @property
    def unified_responses(self) -> Optional[Dict[str, List["UnifiedValueSchema"]]]:
        """Property that returns the unified responses for the record."""
        return self._unified_responses

    def update(
        self, suggestions: Union[SuggestionSchema, List[SuggestionSchema], Dict[str, Any], List[Dict[str, Any]]]
    ) -> None:
        if isinstance(suggestions, (dict, SuggestionSchema)):
            suggestions = [suggestions]
        parsed_suggestions = []
        for suggestion in suggestions:
            if not isinstance(suggestion, SuggestionSchema):
                suggestion = SuggestionSchema(**suggestion)
            parsed_suggestions.append(suggestion)

        suggestions_dict = {suggestion.question_name: suggestion for suggestion in self.suggestions}
        for suggestion in parsed_suggestions:
            if suggestion.question_name in suggestions_dict:
                warnings.warn(
                    f"A suggestion for question `{suggestion.question_name}` has already"
                    " been provided, so the provided suggestion will overwrite it.",
                    category=UserWarning,
                )
            suggestions_dict[suggestion.question_name] = suggestion

        self.__dict__["suggestions"] = tuple(suggestions_dict.values())

    def to_server_payload(self, question_name_to_id: Optional[Dict[str, UUID]] = None) -> Dict[str, Any]:
        """Method that will be used to create the payload that will be sent to Argilla
        to create a `FeedbackRecord` in the `FeedbackDataset`.
        """
        payload = {}
        payload["fields"] = {key: value for key, value in self.fields.items() if value is not None}
        if self.responses:
            payload["responses"] = [response.to_server_payload() for response in self.responses]
        if question_name_to_id:
            payload["suggestions"] = [
                suggestion.to_server_payload(question_name_to_id) for suggestion in self.suggestions
            ]

        if self.vectors:
            payload["vectors"] = self.vectors
        if self.metadata:
            payload["metadata"] = self.metadata
        if self.external_id:
            payload["external_id"] = self.external_id
        return payload


class SortBy(BaseModel):
    field: Union[str, RecordSortField]
    order: Union[str, SortOrder] = SortOrder.asc

    @validator("field", pre=True)
    def check_field_name(cls, field: Union[str, RecordSortField]) -> Union[str, RecordSortField]:
        try:
            return RecordSortField(field)
        except ValueError:
            if field.startswith("metadata."):
                return field
            else:
                raise ValueError(
                    f"{field} is not a valid field name. Supported fields are: {RecordSortField} or metadata.*"
                )

    @validator("order")
    def check_order(cls, order):
        return SortOrder(order)

    @property
    def is_metadata_field(self) -> bool:
        """Returns whether the field is a metadata field."""
        return self.field.startswith("metadata.")

    @property
    def metadata_name(self) -> Optional[str]:
        """Returns the name of the metadata field."""
        if self.field.startswith("metadata."):
            return self.field.split("metadata.")[1]
