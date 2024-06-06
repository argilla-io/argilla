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
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional, Union

from argilla_v1.client.feedback.schemas.enums import LabelsOrder, QuestionTypes
from argilla_v1.client.feedback.schemas.response_values import parse_value_response_for_question
from argilla_v1.client.feedback.schemas.responses import ResponseValue, ValueSchema
from argilla_v1.client.feedback.schemas.suggestions import SuggestionSchema
from argilla_v1.client.feedback.schemas.utils import LabelMappingMixin
from argilla_v1.client.feedback.schemas.validators import title_must_have_value
from argilla_v1.pydantic_v1 import BaseModel, Extra, Field, conint, conlist, root_validator, validator


class QuestionSchema(BaseModel, ABC):
    """Base schema for the `FeedbackDataset` questions. Which means that all the questions
    in the dataset will have at least these fields.

    Args:
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

    Disclaimer:
        You should not use this class directly, but instead use the classes that inherit
        from this one, as they will have the `type` field already defined, and ensured
        to be supported by Argilla.
    """

    name: str = Field(..., regex=r"^(?=.*[a-z0-9])[a-z0-9_-]+$")
    title: Optional[str] = None
    description: Optional[str] = None
    required: bool = True
    type: Optional[QuestionTypes] = Field(..., allow_mutation=False)

    _title_must_have_value = validator("title", always=True, allow_reuse=True)(title_must_have_value)

    class Config:
        validate_assignment = True
        extra = Extra.forbid
        exclude = {"type"}

    @property
    @abstractmethod
    def server_settings(self) -> Dict[str, Any]:
        """Abstract property that should be implemented by the classes that inherit from
        this one, and that will be used to create the `FeedbackDataset` in Argilla.
        """
        ...

    def to_server_payload(self) -> Dict[str, Any]:
        """Method that will be used to create the payload that will be sent to Argilla
        to create a field in the `FeedbackDataset`.
        """
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "required": self.required,
            "settings": self.server_settings,
        }

    def suggestion(self, value: ResponseValue, **kwargs) -> SuggestionSchema:
        """Method that will be used to create a `SuggestionSchema` from the question and a suggested value."""
        value = parse_value_response_for_question(self, value)
        return SuggestionSchema(question_name=self.name, value=value, **kwargs)

    def response(self, value: ResponseValue) -> Dict[str, ValueSchema]:
        """Method that will be used to create a response from the question and a value."""
        value = parse_value_response_for_question(self, value)
        return {self.name: ValueSchema(value=value)}


class TextQuestion(QuestionSchema):
    """Schema for the `FeedbackDataset` text questions, which are the ones that will
    require a text response from the user.

    Args:
        type: The type of the question. Defaults to 'text' and cannot/shouldn't be
            modified.
        use_markdown: Whether the question should be rendered using markdown or not.
            Defaults to False.

    Examples:
        >>> from argilla_v1.client.feedback.schemas.questions import TextQuestion
        >>> TextQuestion(name="text_question", title="Text Question")
    """

    type: Literal[QuestionTypes.text] = Field(QuestionTypes.text.value, allow_mutation=False, const=True)
    use_markdown: bool = False

    @property
    def server_settings(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "use_markdown": self.use_markdown,
        }


class RatingQuestion(QuestionSchema, LabelMappingMixin):
    """Schema for the `FeedbackDataset` rating questions, which are the ones that will
    require a rating response from the user.

    Args:
        type: The type of the question. Defaults to 'rating' and cannot/shouldn't be
            modified.
        values: The list of integer values of the rating question. There is not need
            for the values to be sequential, but they must be unique, contain at least two
            unique integers in the range [0, 10].

    Examples:
        >>> from argilla_v1.client.feedback.schemas.questions import RatingQuestion
        >>> RatingQuestion(name="rating_question", title="Rating Question", values=[1, 2, 3, 4, 5])
    """

    type: Literal[QuestionTypes.rating] = Field(QuestionTypes.rating.value, allow_mutation=False, const=True)
    values: List[int] = Field(..., unique_items=True, ge=0, le=10, min_items=2)

    @property
    def server_settings(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "options": [{"value": value} for value in self.values],
        }


UndefinedType = Literal["undefined"]
UNDEFINED = "undefined"


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
        visible_labels: The number of visible labels in the UI. Defaults to undefined,
            which means that it will be automatically set, otherwise it must be either None
            which means all the labels will be shown, or 3 or greater.
    """

    labels: Union[conlist(str, unique_items=True, min_items=2), Dict[str, str]]
    visible_labels: Union[UndefinedType, conint(ge=3), None] = UNDEFINED

    @validator("labels", pre=True, always=True)
    def labels_dict_must_be_valid(cls, v: Union[List[str], Dict[str, str]]) -> Union[List[str], Dict[str, str]]:
        if isinstance(v, dict):
            assert len(v.keys()) > 1, "ensure this dict has at least 2 items"
            assert len(set(v.values())) == len(v.values()), "ensure this dict has unique values"
        return v

    @root_validator(skip_on_failure=True)
    def visible_labels_must_be_valid(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values.get("visible_labels") == UNDEFINED:
            if len(values.get("labels")) > 20:
                warnings.warn(
                    "Since `visible_labels` has not been provided and the total number"
                    " of labels is greater than 20, `visible_labels` will be set to `20`.",
                    UserWarning,
                    stacklevel=1,
                )
                visible_labels = 20
            else:
                visible_labels = None
        else:
            visible_labels = values.get("visible_labels")
            total_labels = len(values.get("labels"))
            if visible_labels and visible_labels > total_labels:
                if total_labels >= 3:
                    warnings.warn(
                        f"`visible_labels={visible_labels}` is greater than the total number"
                        f" of labels ({total_labels}), so it will be set to `{total_labels}`.",
                        UserWarning,
                        stacklevel=1,
                    )
                    visible_labels = total_labels
                else:
                    warnings.warn(
                        f"`labels={values.get('labels')}` has less than 3 labels, so `visible_labels`"
                        " will be set to `None`, which means that all the labels will be visible.",
                        UserWarning,
                        stacklevel=1,
                    )
                    visible_labels = None
        values["visible_labels"] = visible_labels
        return values

    @property
    def server_settings(self) -> Dict[str, Any]:
        settings = {}
        settings["type"] = self.type
        if isinstance(self.labels, dict):
            settings["options"] = [{"value": key, "text": value} for key, value in self.labels.items()]
        elif isinstance(self.labels, list):
            settings["options"] = [{"value": label, "text": label} for label in self.labels]
        settings["visible_options"] = self.visible_labels
        return settings


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
        >>> from argilla_v1.client.feedback.schemas.questions import LabelQuestion
        >>> LabelQuestion(name="label_question", title="Label Question", labels=["label_1", "label_2"])
    """

    type: Literal[QuestionTypes.label_selection] = Field(
        QuestionTypes.label_selection.value, allow_mutation=False, const=True
    )


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
        labels_order: An optional value that configures the order in which the labels are
            presented in the UI. Possible values are 'natural' and 'suggestion', with 'natural'
            displaying the labels in the natural order in which they were specified, and 'suggestion'
            displaying the labels with priority for those associated with a suggestion.
            The score of the suggestion will be taken into account for ordering if available.
            Defaults to 'natural'.

    Examples:
        >>> from argilla_v1.client.feedback.schemas.questions import MultiLabelQuestion
        >>> MultiLabelQuestion(name="multi_label_question", title="Multi Label Question", labels=["label_1", "label_2"])
    """

    type: Literal[QuestionTypes.multi_label_selection] = Field(
        QuestionTypes.multi_label_selection.value, allow_mutation=False, const=True
    )
    labels_order: LabelsOrder = Field(LabelsOrder.natural, description="The order of the labels in the UI.")

    @property
    def server_settings(self) -> Dict[str, Any]:
        settings = super().server_settings

        settings["options_order"] = self.labels_order

        return settings


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
        >>> from argilla_v1.client.feedback.schemas.questions import RankingQuestion
        >>> RankingQuestion(name="ranking_question", title="Ranking Question", values=["label_1", "label_2"])
    """

    type: Literal[QuestionTypes.ranking] = Field(QuestionTypes.ranking.value, allow_mutation=False, const=True)
    values: Union[conlist(str, unique_items=True, min_items=2), Dict[str, str]]

    @validator("values", always=True)
    def values_dict_must_be_valid(cls, v: Union[List[str], Dict[str, str]]) -> Union[List[str], Dict[str, str]]:
        if isinstance(v, dict):
            assert len(v.keys()) > 1, "ensure this dict has at least 2 items"
            assert len(set(v.values())) == len(v.values()), "ensure this dict has unique values"
        return v

    @property
    def server_settings(self) -> Dict[str, Any]:
        settings = {}
        settings["type"] = self.type
        if isinstance(self.values, dict):
            settings["options"] = [{"value": key, "text": value} for key, value in self.values.items()]
        elif isinstance(self.values, list):
            settings["options"] = [{"value": label, "text": label} for label in self.values]
        return settings


class SpanLabelOption(BaseModel):
    """Schema for the `FeedbackDataset` span label options, which are the ones that will be
    used in the `SpanQuestion` to define the labels that the user can select.

    Args:
        value: The value of the span label. This is the value that will be shown in the UI.
        text: The text of the span label. This is the text that will be shown in the UI.

    Examples:
        >>> from argilla_v1.client.feedback.schemas.questions import SpanLabelOption
        >>> SpanLabelOption(value="span_label_1", text="Span Label 1")
    """

    value: str
    text: Optional[str]
    description: Optional[str]

    def __eq__(self, other):
        return other and self.value == other.value

    @validator("text", pre=True, always=True)
    def default_text_value(cls, v: str, values: Dict[str, Any]) -> str:
        if v is None:
            return values["value"]
        return v


class SpanQuestion(QuestionSchema):
    """Schema for the `FeedbackDataset` span questions, which are the ones that will
    require a span response from the user. More specifically, the user will be asked
    to select a span of text from the input.

    Examples:
        >>> from argilla_v1.client.feedback.schemas.questions import SpanQuestion
        >>> SpanQuestion(name="span_question", field="prompt", title="Span Question", labels=["person", "org"])
    """

    _DEFAULT_MAX_VISIBLE_LABELS = 20
    _MIN_VISIBLE_LABELS = 3

    type: Literal[QuestionTypes.span] = Field(QuestionTypes.span.value, allow_mutation=False, const=True)

    field: str = Field(..., description="The field in the input that the user will be asked to annotate.")
    labels: Union[Dict[str, str], conlist(Union[str, SpanLabelOption], min_items=1, unique_items=True)]
    visible_labels: Union[conint(ge=3), None] = _DEFAULT_MAX_VISIBLE_LABELS
    allow_overlapping: bool = Field(False, description="Configure span to support overlap")

    @validator("labels", pre=True)
    def parse_labels_dict(cls, labels) -> List[SpanLabelOption]:
        if isinstance(labels, dict):
            return [SpanLabelOption(value=label, text=text) for label, text in labels.items()]
        return labels

    @validator("labels", always=True)
    def normalize_labels(cls, v: List[Union[str, SpanLabelOption]]) -> List[SpanLabelOption]:
        return [SpanLabelOption(value=label, text=label) if isinstance(label, str) else label for label in v]

    @validator("labels")
    def labels_must_be_valid(cls, labels: List[SpanLabelOption]) -> List[SpanLabelOption]:
        # This validator is needed since the conlist constraint does not work.
        assert len(labels) > 0, "At least one label must be provided"
        return labels

    @root_validator(skip_on_failure=True)
    def check_visible_labels_value(cls, values) -> Optional[int]:
        visible_labels_key = "visible_labels"

        v = values[visible_labels_key]
        if v is None:
            return values

        msg = None
        number_of_labels = len(values.get("labels", []))

        if cls._MIN_VISIBLE_LABELS > number_of_labels < v:
            msg = f"Since `labels` has less than {cls._MIN_VISIBLE_LABELS} labels, `visible_labels` will be set to `None`."
            v = None
        elif v > number_of_labels:
            msg = (
                f"`visible_labels={v}` is greater than the total number of labels ({number_of_labels}), "
                f"so it will be set to `{number_of_labels}`."
            )
            v = number_of_labels

        if msg:
            warnings.warn(msg, UserWarning, stacklevel=1)

        values[visible_labels_key] = v
        return values

    @property
    def server_settings(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "field": self.field,
            "visible_options": self.visible_labels,
            "allow_overlapping": self.allow_overlapping,
            "options": [label.dict() for label in self.labels],
        }


AllowedQuestionTypes = Union[
    TextQuestion,
    RatingQuestion,
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    SpanQuestion,
]
