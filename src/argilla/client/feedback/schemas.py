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
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union
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
                " issue, unless you're planning to log the response in Argilla, as "
                " it will be automatically set to the active `user_id`.",
            )
        return v


class SuggestionSchema(BaseModel):
    name: str
    type: Optional[Literal["model", "human"]] = None
    score: Optional[float] = None
    value: Any
    agent: Optional[str] = None


class FeedbackRecord(BaseModel):
    """A feedback record.

    Args:
        fields (Dict[str, str]): The fields of the record.
        metadata (Optional[Dict[str, Any]]): The metadata of the record. Defaults to None.
        responses (Optional[List[ResponseSchema]]): The responses of the record. Defaults to None.
        external_id (Optional[str]): The external id of the record. Defaults to None.

    Examples:
        >>> import argilla as rg
        >>> rg.FeedbackRecord(
        ...     fields={"text": "This is the first record", "label": "positive"},
        ...     metadata={"first": True, "nested": {"more": "stuff"}},
        ...     responses=[{"values": {"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}}}],
        ...     external_id="entry-1",
        ... )
        >>> # or use a ResponseSchema directly
        >>> rg.FeedbackRecord(
        ...     fields={"text": "This is the first record", "label": "positive"},
        ...     metadata={"first": True, "nested": {"more": "stuff"}},
        ...     responses=[rg.ResponseSchema(values={"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}}))],
        ...     external_id="entry-1",
        ... )

    """

    id: Optional[UUID] = None
    fields: Dict[str, str]
    metadata: Optional[Dict[str, Any]] = None
    responses: Optional[List[ResponseSchema]] = None
    suggestions: Optional[List[SuggestionSchema]] = None
    external_id: Optional[str] = None

    _unified_responses: Optional[Dict[str, List["UnifiedValueSchema"]]] = PrivateAttr(default={})

    _update: bool = PrivateAttr(default=False)

    @root_validator
    def set_update_flag(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values.get("suggestions") and values.get("id"):
            values["_update"] = True
        if values.get("suggestions") and values.get("id") is None:
            warnings.warn(
                "Ignore the following if you are creating a new `FeedbackDataset` with"
                " `FeedbackRecord`s, or if you are just working with a `FeedbackRecord`."
                " Otherwise, if the `FeedbackRecord` is already pushed"
                " to Argilla, note that `suggestions` have been provided, but the `id`"
                " is not set, which means that the `FeedbackRecord` has been pushed to"
                " Argilla, but hasn't been fetched, so the `id` is missing. To solve that,"
                " you can simply call `FeedbackDataset.fetch_records()` to fetch them and"
                " automatically set the `id`, to add the `suggestions` on top of that."
            )
        return values

    class Config:
        extra = Extra.forbid
        validate_assignment = True
        exclude = {"_unified_responses", "_update"}


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
