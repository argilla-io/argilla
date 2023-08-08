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

import httpx
from pydantic import BaseModel, Extra, Field, PrivateAttr, StrictInt, StrictStr, conint, validator

from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.sdk.v1.records import api as records_api_v1

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
    rank: conint(ge=1)


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
    values: Dict[str, ValueSchema]
    status: Literal["submitted", "discarded"] = "submitted"

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


class SuggestionSchema(BaseModel):
    """Schema for the suggestions for the questions related to the record.

    Args:
        question_id: ID of the question in Argilla. Defaults to None, and is automatically
           fulfilled internally once the question is pushed to Argilla.
        question_name: name of the question.
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

    question_id: Optional[UUID] = None
    question_name: str
    type: Optional[Literal["model", "human"]] = None
    score: Optional[float] = None
    value: Any
    agent: Optional[str] = None

    class Config:
        extra = Extra.forbid


class FeedbackRecord(BaseModel):
    """Schema for the records of a `FeedbackDataset`.

    Args:
        fields: Fields that match the `FeedbackDataset` defined fields. So this attribute
            contains the actual information shown in the UI for each record, being the
            record itself.
        metadata: Metadata to be included to enrich the information for a given record.
            Note that the metadata is not shown in the UI so you'll just be able to see
            that programatically after pulling the records. Defaults to None.
        responses: Responses given by either the current user, or one or a collection of
            users that must exist in Argilla. Each response corresponds to one of the
            `FeedbackDataset` questions, so the values should match the question type.
            Defaults to None.
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

    fields: Dict[str, str]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    responses: List[ResponseSchema] = Field(default_factory=list)
    suggestions: Union[Tuple[SuggestionSchema], List[SuggestionSchema]] = Field(
        default_factory=tuple, allow_mutation=False
    )
    external_id: Optional[str] = None

    _unified_responses: Optional[Dict[str, List["UnifiedValueSchema"]]] = PrivateAttr(default_factory=dict)

    @validator("suggestions", always=True)
    def normalize_suggestions(cls, values: Any) -> Tuple:
        if not isinstance(values, tuple):
            return tuple([v for v in values])
        return values

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

    def set_suggestions(
        self, suggestions: Union[SuggestionSchema, List[SuggestionSchema], Dict[str, Any], List[Dict[str, Any]]]
    ) -> None:
        warnings.warn(
            "`set_suggestions` is deprected in favor of `update` and will be removed in a future"
            " release.\n`set_suggestions` will be deprecated in Argilla v1.15.0, please"
            " use `update` instead.",
            DeprecationWarning,
            stacklevel=1,
        )
        self.update(suggestions=suggestions)

    class Config:
        extra = Extra.forbid
        validate_assignment = True
        exclude = {"_unified_responses"}


class RemoteFeedbackRecord(FeedbackRecord):
    """Schema for the records of a `RemoteFeedbackDataset`.

    Note this schema shouldn't be instantiated directly, but just internally by the
    `RemoteFeedbackDataset` class when fetching records from Argilla.

    Args:
        id: The ID of the record in Argilla. Defaults to None, and is automatically
            fulfilled internally once the record is pushed to Argilla.
        client: The Argilla client to use to push the record to Argilla. Is shared with
            the `RemoteFeedbackDataset` that created this record.
        name2id: A dictionary that maps the question names to their corresponding IDs.
    """

    client: httpx.Client
    name2id: Dict[str, UUID]

    id: UUID

    def update(
        self, suggestions: Union[SuggestionSchema, List[SuggestionSchema], Dict[str, Any], List[Dict[str, Any]]]
    ) -> None:
        """Update a `RemoteFeedbackRecord`. Currently just `suggestions` are supported.

        Note that this method will update the record in Argilla directly.

        Args:
            suggestions: can be a single `SuggestionSchema`, a list of `SuggestionSchema`,
                a single dictionary, or a list of dictionaries. If a dictionary is provided,
                it will be converted to a `SuggestionSchema` internally.
        """
        super().update(suggestions)
        for suggestion in self.suggestions:
            suggestion.question_id = self.name2id[suggestion.question_name]
            datasets_api_v1.set_suggestion(
                client=self.client, record_id=self.id, **suggestion.dict(exclude_none=True, exclude={"question_name"})
            )

    def set_suggestions(
        self, suggestions: Union[SuggestionSchema, List[SuggestionSchema], Dict[str, Any], List[Dict[str, Any]]]
    ) -> None:
        """Deprecated, use `update` instead."""
        warnings.warn(
            "`set_suggestions` is deprected in favor of `update` and will be removed in a future"
            " release.\n`set_suggestions` will be deprecated in Argilla v1.15.0, please"
            " use `update` instead.",
            DeprecationWarning,
            stacklevel=1,
        )
        self.update(suggestions=suggestions)

    def delete(self) -> FeedbackRecord:
        """Deletes the `RemoteFeedbackRecord` from Argilla.

        Returns:
            The deleted record formatted as a `FeedbackRecord`.
        """
        try:
            response = records_api_v1.delete_record(client=self.client, id=self.id)
        except Exception as e:
            raise RuntimeError(f"Failed to delete record with ID `{self.id}` from Argilla.") from e
        return FeedbackRecord(**response.parsed.dict(exclude={"id", "inserted_at", "updated_at"}, exclude_none=True))

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        exclude = {"_unified_responses", "client", "name2id"}
