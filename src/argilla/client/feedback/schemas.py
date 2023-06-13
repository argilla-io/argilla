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
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pydantic import (
    BaseModel,
    Extra,
    Field,
    StrictInt,
    StrictStr,
    conint,
    conlist,
    root_validator,
    validator,
)

FETCHING_BATCH_SIZE = 250
PUSHING_BATCH_SIZE = 32


class ValueSchema(BaseModel):
    """A value schema for a record.

    Args:
        value (Union[StrictStr, StrictInt, List[str]]): The value of the record.

    Examples:
        >>> import argilla as rg
        >>> value = rg.ValueSchema(value="Yes")
        >>> # or use a dict
        >>> value = {"value": "Yes"}

    """

    value: Union[StrictStr, StrictInt, List[str]]


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
                stacklevel=2,
            )
        return v


class FeedbackRecord(BaseModel):
    """A feedback record.

    Args:
        fields (Dict[str, str]): The fields of the record.
        responses (Optional[Union[ResponseSchema, List[ResponseSchema]]]): The responses of the record. Defaults to None.
        external_id (Optional[str]): The external id of the record. Defaults to None.

    Examples:
        >>> import argilla as rg
        >>> rg.FeedbackRecord(
        ...     fields={"text": "This is the first record", "label": "positive"},
        ...     responses=[{"values": {"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}}}],
        ...     external_id="entry-1",
        ... )
        >>> # or use a ResponseSchema directly
        >>> rg.FeedbackRecord(
        ...     fields={"text": "This is the first record", "label": "positive"},
        ...     responses=[rg.ResponseSchema(values={"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}}))],
        ...     external_id="entry-1",
        ... )

    """

    fields: Dict[str, str]
    responses: Optional[Union[ResponseSchema, List[ResponseSchema]]] = None
    external_id: Optional[str] = None

    @validator("responses", always=True)
    def responses_must_be_a_list(cls, v: Optional[Union[ResponseSchema, List[ResponseSchema]]]) -> List[ResponseSchema]:
        if not v:
            return []
        if isinstance(v, ResponseSchema):
            return [v]
        return v

    class Config:
        extra = Extra.ignore


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

    name: str
    title: Optional[str] = None
    required: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict, allow_mutation=False)

    @validator("title", always=True)
    def title_must_have_value(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values.get("name").capitalize()
        return v

    class Config:
        validate_assignment = True
        extra = Extra.forbid


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

    settings: Dict[str, Any] = Field({"type": "text"}, allow_mutation=False)
    use_markdown: bool = False

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["use_markdown"] = values.get("use_markdown", False)
        return values


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

    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    required: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict, allow_mutation=False)

    @validator("title", always=True)
    def title_must_have_value(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values.get("name").capitalize()
        return v

    class Config:
        validate_assignment = True
        extra = Extra.forbid


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

    settings: Dict[str, Any] = Field({"type": "text", "use_markdown": False}, allow_mutation=False)
    use_markdown: bool = False

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
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

    settings: Dict[str, Any] = Field({"type": "rating"}, allow_mutation=False)
    values: List[int] = Field(unique_items=True, min_items=2)

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["options"] = [{"value": value} for value in values.get("values")]
        return values


class _LabelQuestion(QuestionSchema):
    settings: Dict[str, Any] = Field(default_factory=dict, allow_mutation=False)
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

    settings: Dict[str, Any] = Field({"type": "label_selection"})


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

    settings: Dict[str, Any] = Field({"type": "multi_label_selection"})


AllowedFieldTypes = TextField
AllowedQuestionTypes = Union[TextQuestion, RatingQuestion, LabelQuestion, MultiLabelQuestion]


class FeedbackDatasetConfig(BaseModel):
    """`FeedbackDatasetConfig`

    Args:
        fields (List[AllowedFieldTypes]): The fields of the feedback dataset.
        questions (List[AllowedQuestionTypes]): The questions of the feedback dataset.
        guidelines (Optional[str]): the guidelines of the feedback dataset. Defaults to None.

    Examples:
        >>> import argilla as rg
        >>> config = rg.FeedbackDatasetConfig(
        ...     fields=[
        ...         rg.TextField(name="text", title="Human prompt"),
        ...     ],
        ...     questions =[
        ...         rg.TextQuestion(
        ...             name="question-1",
        ...             description="This is the first question",
        ...             required=True,
        ...         ),
        ...         rg.RatingQuestion(
        ...             name="question-2",
        ...             description="This is the second question",
        ...             required=True,
        ...             values=[1, 2, 3, 4, 5],
        ...         ),
        ...         rg.LabelQuestion(
        ...             name="relevant",
        ...             title="Is the response relevant for the given prompt?",
        ...             labels=["Yes","No"],
        ...             required=True,
        ...             visible_labels=None
        ...         ),
        ...         rg.MultiLabelQuestion(
        ...             name="content_class",
        ...             title="Does the response include any of the following?",
        ...             description="Select all that apply",
        ...             labels={"cat-1": "Category 1" , "cat-2": "Category 2"},
        ...             required=False,
        ...             visible_labels=4
        ...         ),
        ...     ],
        ...     guidelines="Add some guidelines for the annotation team here."
        ... )

    """

    fields: List[AllowedFieldTypes]
    questions: List[AllowedQuestionTypes]
    guidelines: Optional[str] = None

    class Config:
        smart_union = True
