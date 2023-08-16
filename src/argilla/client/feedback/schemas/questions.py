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
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Extra, Field, conint, conlist, root_validator, validator

from argilla.client.feedback.schemas.utils import LabelMappingMixin
from argilla.client.feedback.schemas.validators import title_must_have_value

QuestionTypes = Literal["text", "rating", "label_selection", "multi_label_selection", "ranking"]


class QuestionSchema(BaseModel):
    """Base schema for the `FeedbackDataset` questions. Which means that all the questions
    in the dataset will have at least these fields.

    Args:
        id: The ID of the question in Argilla. Defaults to None, and is automatically
            fulfilled internally once the question is pushed to Argilla.
        name: The name of the question. This is the only required field.
        title: The title of the question. If not provided, it will be capitalized from
            the `name` field. And its what will be shown in the UI.
        description: The description of the question. Defaults to None, and is not shown
            in the UI, otherwise, it will be shown in the tooltip close to each question.
        required: Whether the question is required or not. Defaults to True. Note that at
            least one question must be required.
        type: The type of the question. Defaults to None, and ideally it should be defined
            in the class inheriting from this one to be able to use a discriminated union
            based on the `type` field.
        settings: The settings of the question. Defaults to an empty dict, and it is
            automatically fulfilled internally before the question is pushed to Argilla,
            as the `settings` is part of the payload that will be sent to Argilla.

    Disclaimer:
        You should not use this class directly, but instead use the classes that inherit
        from this one, as they will have the `type` field already defined, and ensured
        to be supported by Argilla.
    """

    id: Optional[UUID] = None
    name: str = Field(..., regex=r"^(?=.*[a-z0-9])[a-z0-9_-]+$")
    title: Optional[str] = None
    description: Optional[str] = None
    required: bool = True
    type: Optional[QuestionTypes] = None
    settings: Dict[str, Any] = Field(default_factory=dict, allow_mutation=False)

    _title_must_have_value = validator("title", always=True, allow_reuse=True)(title_must_have_value)

    class Config:
        validate_assignment = True
        extra = Extra.forbid
        exclude = {"id", "type"}


# TODO(alvarobartt): add `XResponse` (e.g. `TextResponse`) classes
class TextQuestion(QuestionSchema):
    """Schema for the `FeedbackDataset` text questions, which are the ones that will
    require a text response from the user.

    Args:
        type: The type of the question. Defaults to 'text' and cannot/shouldn't be
            modified.
        use_markdown: Whether the question should be rendered using markdown or not.
            Defaults to False.

    Examples:
        >>> from argilla.client.feedback.schemas.questions import TextQuestion
        >>> TextQuestion(name="text_question", title="Text Question")
    """

    type: Literal["text"] = Field("text", allow_mutation=False)
    use_markdown: bool = False

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["type"] = values.get("type")
        values["settings"]["use_markdown"] = values.get("use_markdown", False)
        return values


class RatingQuestion(QuestionSchema, LabelMappingMixin):
    """Schema for the `FeedbackDataset` rating questions, which are the ones that will
    require a rating response from the user.

    Args:
        type: The type of the question. Defaults to 'rating' and cannot/shouldn't be
            modified.
        values: The list of interger values of the rating question. There is not need
            for the values to be sequential, but they must be unique, contain at least two
            unique integers in the range [1, 10].

    Examples:
        >>> from argilla.client.feedback.schemas.questions import RatingQuestion
        >>> RatingQuestion(name="rating_question", title="Rating Question", values=[1, 2, 3, 4, 5])
    """

    type: Literal["rating"] = Field("rating", allow_mutation=False)
    values: List[int] = Field(unique_items=True, min_items=2)

    @validator("values")
    def check_values(cls, values: List[int]):
        if len(values) > 10:
            warnings.warn(
                "`values` list contains more than 10 elements, which is not supported from Argilla 1.14.0 onwards. "
                "Please, make sure `values` is a list with more than 1 element and less or equal than 10 "
                "before pushing the dataset into Argilla. Otherwise, the `push_to_argilla` method will fail",
            )
        for value in values:
            if not 1 <= value <= 10:
                warnings.warn(
                    "At least one `value` in `values` is out of range [1, 10], "
                    "which is not supported from Argilla 1.14.0 onwards. "
                    "Please, make sure `values` is a list with unique values within the range [1, 10] "
                    "before pushing the dataset into Argilla. Otherwise, the `push_to_argilla` method will fail. ",
                )
                break
        return values

    @root_validator(skip_on_failure=True)
    def update_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["settings"]["type"] = values.get("type")
        values["settings"]["options"] = [{"value": value} for value in values.get("values")]
        return values


class _LabelQuestion(QuestionSchema, LabelMappingMixin):
    """Protected schema for the `FeedbackDataset` label questions, which are the ones that
    will require a label response from the user. This class should not be used directly,
    but instead use the classes that inherit from this one, which in this case are:
    `LabelSelectionQuestion` and `MultiLabelSelectionQuestion`.

    Args:
        type: The type of the question. Defaults to None and cannot/shouldn't be modified.
        labels: The list of labels of the label question. The labels must be unique, and
            the list must contain at least two unique labels. Additionally, `labels` can
            also be a dictionary of labels, where the keys are the labels, and the values
            are the labels that will be shown in the UI.
        visible_labels: The number of visible labels in the UI. Defaults to 20, and must
            be 3 or greater.
    """

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


class LabelQuestion(_LabelQuestion):
    """Schema for the `FeedbackDataset` label questions, which are the ones that will
    require a label response from the user. This class should be used when the user can
    only select one label.

    Args:
        type: The type of the question. Defaults to 'label_selection' and cannot/shouldn't
            be modified.
        labels: The list of labels of the label question. The labels must be unique, and
            the list must contain at least two unique labels. Additionally, `labels` can
            also be a dictionary of labels, where the keys are the labels, and the values
            are the labels that will be shown in the UI.
        visible_labels: The number of visible labels in the UI. Defaults to 20, and must
            be 3 or greater.

    Examples:
        >>> from argilla.client.feedback.schemas.questions import LabelQuestion
        >>> LabelQuestion(name="label_question", title="Label Question", labels=["label_1", "label_2"])
    """

    type: Literal["label_selection"] = Field("label_selection", allow_mutation=False)


class MultiLabelQuestion(_LabelQuestion):
    """Schema for the `FeedbackDataset` label questions, which are the ones that will
    require a label response from the user. This class should be used when the user can
    select multiple labels.

    Args:
        type: The type of the question. Defaults to 'multi_label_selection' and
            cannot/shouldn't be modified.
        labels: The list of labels of the label question. The labels must be unique, and
            the list must contain at least two unique labels. Additionally, `labels` can
            also be a dictionary of labels, where the keys are the labels, and the values
            are the labels that will be shown in the UI.
        visible_labels: The number of visible labels in the UI. Defaults to 20, and must
            be 3 or greater.

    Examples:
        >>> from argilla.client.feedback.schemas.questions import MultiLabelQuestion
        >>> MultiLabelQuestion(name="multi_label_question", title="Multi Label Question", labels=["label_1", "label_2"])
    """

    type: Literal["multi_label_selection"] = Field("multi_label_selection", allow_mutation=False)


class RankingQuestion(QuestionSchema, LabelMappingMixin):
    """Schema for the `FeedbackDataset` ranking questions, which are the ones that will
    require a ranking response from the user. More specifically, the user will be asked
    to rank the labels, all the labels need to be assigned (if either the question is
    required or if at least one label has been ranked), and there can be ties/draws.

    Args:
        type: The type of the question. Defaults to 'ranking' and cannot/shouldn't be
            modified.
        values: The list of labels of the ranking question. The labels must be unique, and
            the list must contain at least two unique labels. Additionally, `labels` can
            also be a dictionary of labels, where the keys are the labels, and the values
            are the labels that will be shown in the UI.

    Examples:
        >>> from argilla.client.feedback.schemas.questions import RankingQuestion
        >>> RankingQuestion(name="ranking_question", title="Ranking Question", labels=["label_1", "label_2"])
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
