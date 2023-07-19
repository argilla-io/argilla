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

from pydantic import (
    BaseModel,
    Extra,
    Field,
    PrivateAttr,
    StrictInt,
    StrictStr,
    conint,
    conlist,
    root_validator,
    validator,
)

if TYPE_CHECKING:
    from argilla.client.feedback.unification import UnifiedValueSchema


class RankingValueSchema(BaseModel):
    """Schema for the `RankingQuestion` response value.

    Note: we may have more than one record in the same rank.

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
    """A response schema for a record.

    Args:
        user_id (Optional[UUID]): The user id of the response. Defaults to None.
        values (Dict[str, ValueSchema]): The values of the response. Defaults to None.
        status (Literal["submitted", "discarded"]): The status of the response. It can be either `submitted` or `discarded`. Defaults to "submitted".

    Examples:
        >>> import argilla as rg
        >>> response = rg.ResponseSchema(
        ...     user_id="user_id",
        ...     values={"question-1": {"value": "response-1"}}
        ... )
        >>> # or use a ValueSchema directly
        >>> response = rg.ResponseSchema(
        ...     user_id="user_id",
        ...     values={"question-1": rg.ValueSchema(value="response-1")}
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
        >>> import argilla as rg
        >>> rg.SuggestionSchema(
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
    """Schema for the records of a `FeedbackDataset` in Argilla.

    Args:
        id: The ID of the record in Argilla. Defaults to None, and is automatically
            fulfilled internally once the record is pushed to Argilla.
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
        >>> from argilla.client.feedback.schemas import FeedbackRecord, ResponseSchema, ValueSchema
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

    id: Optional[UUID] = None
    fields: Dict[str, str]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    responses: List[ResponseSchema] = Field(default_factory=list)
    suggestions: Union[Tuple[SuggestionSchema], List[SuggestionSchema]] = Field(
        default_factory=tuple, allow_mutation=False
    )
    external_id: Optional[str] = None

    _unified_responses: Optional[Dict[str, List["UnifiedValueSchema"]]] = PrivateAttr(default_factory=dict)
    _updated: bool = PrivateAttr(default=False)

    @validator("suggestions", always=True)
    def normalize_suggestions(cls, values: Any) -> Tuple:
        if not isinstance(values, tuple):
            return tuple([v for v in values])
        return values

    def set_suggestions(
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
        if self.id and not self._updated:
            self._updated = True

    def _reset_updated(self) -> None:
        self._updated = False

    class Config:
        extra = Extra.forbid
        validate_assignment = True
        exclude = {"_unified_responses", "_updated"}


FieldTypes = Literal["text"]


class FieldSchema(BaseModel):
    """A field schema for a feedback dataset.

    Args:
        name (str): The name of the field.
        title (Optional[str]): The title of the field. Defaults to None.
        required (bool): Whether the field is required or not. Defaults to True.

    Examples:
        >>> import argilla as rg
        >>> field = rg.FieldSchema(
        ...     name="text",
        ...     title="Human prompt",
        ...     required=True
        ... )

    """

    id: Optional[UUID] = None
    name: str
    title: Optional[str] = None
    required: bool = True
    type: Optional[FieldTypes] = None
    settings: Dict[str, Any] = Field(default_factory=dict, allow_mutation=False)

    @validator("title", always=True)
    def title_must_have_value(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values.get("name").capitalize()
        return v

    class Config:
        validate_assignment = True
        extra = Extra.forbid
        exclude = {"id", "type"}


class TextField(FieldSchema):
    """A text field schema for a feedback dataset.

    Args:
        name (str): The name of the field.
        title (Optional[str]): The title of the field. Defaults to None.
        required (bool): Whether the field is required or not. Defaults to True.
        use_markdown (bool): Whether the field should use markdown or not. Defaults to False.

    Examples:
        >>> import argilla as rg
        >>> field = rg.FieldSchema(
        ...     name="text",
        ...     title="Human prompt",
        ...     required=True,
        ...     use_markdown=True
        ... )

    """

    type: Literal["text"] = "text"
    use_markdown: bool = False

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["type"] = values.get("type")
        values["settings"]["use_markdown"] = values.get("use_markdown", False)
        return values


QuestionTypes = Literal["text", "rating", "label_selection", "multi_label_selection", "ranking"]


class QuestionSchema(BaseModel):
    """A question schema for a feedback dataset.

    Args:
        name (str): The name of the question.
        title (Optional[str]): The title of the question. Defaults to None.
        description (Optional[str]): The description of the question. Defaults to None.
        required (bool): Whether the question is required or not. Defaults to True.

    Examples:
        >>> import argilla as rg
        >>> question = rg.QuestionSchema(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True
        ... )

    """

    id: Optional[UUID] = None
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    required: bool = True
    type: Optional[QuestionTypes] = None
    settings: Dict[str, Any] = Field(default_factory=dict, allow_mutation=False)

    @validator("title", always=True)
    def title_must_have_value(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values.get("name").capitalize()
        return v

    class Config:
        validate_assignment = True
        extra = Extra.forbid
        exclude = {"id", "type"}


# TODO(alvarobartt): add `TextResponse` and `RatingResponse` classes
class TextQuestion(QuestionSchema):
    """A text question schema for a feedback dataset.

    Args:
        name (str): The name of the question.
        title (Optional[str]): The title of the question. Defaults to None.
        description (Optional[str]): The description of the question. Defaults to None.
        required (bool): Whether the question is required or not. Defaults to True.
        use_markdown (bool): Whether the field should use markdown or not. Defaults to False.

    Examples:
        >>> import argilla as rg
        >>> question = rg.TextQuestion(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True,
        ...     use_markdown=True
        ... )

    """

    type: Literal["text"] = Field("text", allow_mutation=False)
    use_markdown: bool = False

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["type"] = values.get("type")
        values["settings"]["use_markdown"] = values.get("use_markdown", False)
        return values


class RatingQuestion(QuestionSchema):
    """A rating question schema for a feedback dataset.

    Args:
        name (str): The name of the question.
        title (Optional[str]): The title of the question. Defaults to None.
        description (Optional[str]): The description of the question. Defaults to None.
        required (bool): Whether the question is required or not. Defaults to True.
        values (List[int]): The values of the rating question.

    Examples:
        >>> import argilla as rg
        >>> question = rg.RatingQuestion(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True,
        ...     values=[1, 2, 3, 4, 5]
        ... )

    """

    type: Literal["rating"] = Field("rating", allow_mutation=False)
    values: List[int] = Field(unique_items=True, min_items=2)

    @property
    def __all_labels__(self):
        return [entry["value"] for entry in self.settings["options"]]

    @property
    def __label2id__(self):
        return {label: idx for idx, label in enumerate(self.__all_labels__)}

    @property
    def __id2label__(self):
        return {idx: label for idx, label in enumerate(self.__all_labels__)}

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["type"] = values.get("type")
        values["settings"]["options"] = [{"value": value} for value in values.get("values")]
        return values


class _LabelQuestion(QuestionSchema):
    labels: Union[conlist(str, unique_items=True, min_items=2), Dict[str, str]]
    visible_labels: Optional[conint(ge=3)] = 20

    @validator("labels", always=True)
    def labels_dict_must_be_valid(cls, v: Union[List[str], Dict[str, str]]) -> Union[List[str], Dict[str, str]]:
        if isinstance(v, dict):
            assert len(v.keys()) > 1, "ensure this dict has at least 2 items"
            assert len(set(v.values())) == len(v.values()), "ensure this dict has unique values"
        return v

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["type"] = values.get("type")
        if isinstance(values.get("labels"), dict):
            values["settings"]["options"] = [
                {"value": key, "text": value} for key, value in values.get("labels").items()
            ]
        if isinstance(values.get("labels"), list):
            values["settings"]["options"] = [{"value": label, "text": label} for label in values.get("labels")]
        values["settings"]["visible_options"] = values.get(
            "visible_labels"
        )  # `None` is a possible value, which means all labels are visible
        return values

    @property
    def __all_labels__(self):
        return [entry["value"] for entry in self.settings["options"]]

    @property
    def __label2id__(self):
        return {label: idx for idx, label in enumerate(self.__all_labels__)}

    @property
    def __id2label__(self):
        return {idx: label for idx, label in enumerate(self.__all_labels__)}


class LabelQuestion(_LabelQuestion):
    """A label question schema for a feedback dataset.

    Args:
        name (str): The name of the question.
        title (Optional[str]): The title of the question. Defaults to None.
        description (Optional[str]): The description of the question. Defaults to None.
        required (bool): Whether the question is required or not. Defaults to True.
        labels (Union[Dict[str, str],conlist(str)]): The labels of the label question.
        visible_labels (conint(ge=3)): The number of visible labels of the label question. Defaults to 20.
            visible_labels=None implies that ALL the labels will be shown by default, which is not recommended if labels>20

    Examples:
        >>> import argilla as rg
        >>> question = rg.LabelQuestion(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True,
        ...     labels=["Yes", "No"],
        ...     visible_labels=None
        ... )
        >>> # or use a dict
        >>> question = rg.LabelQuestion(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True,
        ...     labels={"yes": "Yes", "no": "No"},
        ...     visible_labels=None
        ... )

    """

    type: Literal["label_selection"] = Field("label_selection", allow_mutation=False)


class MultiLabelQuestion(_LabelQuestion):
    """A multi label question schema for a feedback dataset.

    Args:
        name (str): The name of the question.
        title (Optional[str]): The title of the question. Defaults to None.
        description (Optional[str]): The description of the question. Defaults to None.
        required (bool): Whether the question is required or not. Defaults to True.
        labels (Union[Dict[str, str],conlist(str)]): The labels of the label question.
        visible_labels (conint(ge=3)): The number of visible labels of the label question. Defaults to 20.
            visible_labels=None implies that ALL the labels will be shown by default, which is not recommended if labels>20

    Examples:
        >>> import argilla as rg
        >>> question = rg.MultiLabelQuestion(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True,
        ...     labels=["Yes", "No"],
        ...     visible_labels=None
        ... )
        >>> # or use a dict
        >>> question = rg.MultiLabelQuestion(
        ...     name="relevant",
        ...     title="Is the response relevant for the given prompt?",
        ...     description="Select all that apply",
        ...     required=True,
        ...     labels={"yes": "Yes", "no": "No"},
        ...     visible_labels=None
        ... )

    """

    type: Literal["multi_label_selection"] = Field("multi_label_selection", allow_mutation=False)


class RankingQuestion(QuestionSchema):
    """Schema for the `RankingQuestion` question-type.

    Args:
        settings: The settings for the question, including the type and options.
        values: The values for the question, to be formatted and included as part of
            the settings.

    Examples:
        >>> import argilla as rg
        >>> question = rg.RankingQuestion(
        ...     values=["Yes", "No"]
        ... )
        RankingQuestion(
            settings={
                'type': 'ranking',
                'options': [
                    {'value': 'Yes', 'text': 'Yes'},
                    {'value': 'No', 'text': 'No'}
                ]
            },
            values=['Yes', 'No']
        )
    """

    type: Literal["ranking"] = Field("ranking", allow_mutation=False)
    values: Union[conlist(str, unique_items=True, min_items=2), Dict[str, str]]

    @validator("values", always=True)
    def values_dict_must_be_valid(cls, v: Union[List[str], Dict[str, str]]) -> Union[List[str], Dict[str, str]]:
        if isinstance(v, dict):
            assert len(v.keys()) > 1, "ensure this dict has at least 2 items"
            assert len(set(v.values())) == len(v.values()), "ensure this dict has unique values"
        return v

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["type"] = values.get("type")
        if isinstance(values.get("values"), dict):
            values["settings"]["options"] = [
                {"value": key, "text": value} for key, value in values.get("values").items()
            ]
        if isinstance(values.get("values"), list):
            values["settings"]["options"] = [{"value": value, "text": value} for value in values.get("values")]
        return values

    @property
    def __all_labels__(self):
        return [entry["value"] for entry in self.settings["options"]]

    @property
    def __label2id__(self):
        return {label: idx for idx, label in enumerate(self.__all_labels__)}

    @property
    def __id2label__(self):
        return {idx: label for idx, label in enumerate(self.__all_labels__)}
