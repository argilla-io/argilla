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

from typing import Dict, List, Literal, Optional, Union, TYPE_CHECKING

from argilla import Argilla
from argilla._api import QuestionsAPI
from argilla._models._settings._questions import (
    QuestionModel,
    QuestionSettings,
    LabelQuestionSettings,
    MultiLabelQuestionSettings,
    TextQuestionSettings,
    RatingQuestionSettings,
    RankingQuestionSettings,
    SpanQuestionSettings,
)
from argilla.settings._common import SettingsPropertyBase

if TYPE_CHECKING:
    from argilla.datasets import Dataset

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

__all__ = [
    "LabelQuestion",
    "MultiLabelQuestion",
    "RankingQuestion",
    "TextQuestion",
    "RatingQuestion",
    "SpanQuestion",
    "QuestionType",
]


class QuestionBase(SettingsPropertyBase):
    _model: QuestionModel
    _api: QuestionsAPI
    _dataset: Optional["Dataset"]

    def __init__(
        self,
        name: str,
        settings: QuestionSettings,
        title: Optional[str] = None,
        required: Optional[bool] = True,
        description: Optional[str] = None,
        _client: Optional[Argilla] = None,
    ):
        client = _client or Argilla._get_default()

        super().__init__(api=client.api.questions, client=client)

        self._dataset = None
        self._model = QuestionModel(
            name=name,
            settings=settings,
            title=title,
            required=required,
            description=description,
        )

    @classmethod
    def from_model(cls, model: QuestionModel) -> "Self":
        instance = cls(name=model.name)  # noqa
        instance._model = model

        return instance

    @classmethod
    def from_dict(cls, data: dict) -> "Self":
        model = QuestionModel(**data)
        return cls.from_model(model)

    @property
    def dataset(self) -> "Dataset":
        return self._dataset

    @dataset.setter
    def dataset(self, value: "Dataset") -> None:
        self._dataset = value
        self._model.dataset_id = self._dataset.id
        self._with_client(self._dataset._client)

    def _with_client(self, client: "Argilla") -> "Self":
        # TODO: Review and simplify. Maybe only one of them is required
        self._client = client
        self._api = self._client.api.questions

        return self

    @staticmethod
    def _render_values_as_options(values: Union[List[str], List[int], Dict[str, str]]) -> List[Dict[str, str]]:
        """Render values as options for the question so that the model conforms to the API schema"""
        if isinstance(values, dict):
            return [{"text": value, "value": key} for key, value in values.items()]
        elif isinstance(values, list) and all(isinstance(value, str) for value in values):
            return [{"text": label, "value": label} for label in values]
        elif isinstance(values, list) and all(isinstance(value, int) for value in values):
            return [{"value": value} for value in values]
        else:
            raise ValueError(
                "Invalid labels format. Please provide a list of strings or a dictionary of key-value pairs."
            )

    @staticmethod
    def _render_options_as_values(options: List[dict]) -> Dict[str, str]:
        """Render options as values for the question so that the model conforms to the API schema"""
        values = {}
        for option in options:
            if "text" in option:
                values[option["value"]] = option["text"]
            else:
                values[option["value"]] = option["value"]
        return values

    @classmethod
    def _render_options_as_labels(cls, options: List[Dict[str, str]]) -> List[str]:
        """Render values as labels for the question so that they can be returned as a list of strings"""
        return list(cls._render_options_as_values(options=options).keys())


class LabelQuestion(QuestionBase):
    def __init__(
        self,
        name: str,
        labels: Union[List[str], Dict[str, str]],
        title: Optional[str] = None,
        description: Optional[str] = None,
        required: bool = True,
        visible_labels: Optional[int] = None,
        client: Optional[Argilla] = None,
    ) -> None:
        """ Define a new label question for `Settings` of a `Dataset`. A label \
            question is a question where the user can select one label from \
            a list of available labels.

        Parameters:
            name (str): The name of the question to be used as a reference.
            labels (Union[List[str], Dict[str, str]]): The list of available labels for the question, or a
                dictionary of key-value pairs where the key is the label and the value is the label name displayed in the UI.
            title (Optional[str]): The title of the question to be shown in the UI.
            description (Optional[str]): The description of the question to be shown in the UI.
            required (bool): If the question is required for a record to be valid. At least one question must be required.
            visible_labels (Optional[int]): The number of visible labels for the question to be shown in the UI. \
                Setting it to None show all options.
        """

        super().__init__(
            name=name,
            title=title,
            required=required,
            description=description,
            settings=LabelQuestionSettings(
                options=self._render_values_as_options(labels),
                visible_options=visible_labels,
            ),
            _client=client,
        )

    ##############################
    # Public properties
    ##############################

    @property
    def labels(self) -> List[str]:
        return self._render_options_as_labels(self._model.settings.options)

    @labels.setter
    def labels(self, labels: List[str]) -> None:
        self._model.settings.options = self._render_values_as_options(labels)

    @property
    def visible_labels(self) -> Optional[int]:
        return self._model.settings.visible_options

    @visible_labels.setter
    def visible_labels(self, visible_labels: Optional[int]) -> None:
        self._model.settings.visible_options = visible_labels

    @classmethod
    def from_model(cls, model: QuestionModel) -> "Self":
        instance = cls(name=model.name, labels=cls._render_options_as_labels(model.settings.options))  # noqa
        instance._model = model

        return instance


class MultiLabelQuestion(LabelQuestion):
    def __init__(
        self,
        name: str,
        labels: Union[List[str], Dict[str, str]],
        visible_labels: Optional[int] = None,
        labels_order: Literal["natural", "suggestion"] = "natural",
        title: Optional[str] = None,
        description: Optional[str] = None,
        required: bool = True,
        client: Optional[Argilla] = None,
    ) -> None:
        """Create a new multi-label question for `Settings` of a `Dataset`. A \
            multi-label question is a question where the user can select multiple \
            labels from a list of available labels.

        Parameters:
            name (str): The name of the question to be used as a reference.
            labels (Union[List[str], Dict[str, str]]): The list of available labels for the question, or a \
                dictionary of key-value pairs where the key is the label and the value is the label name displayed in the UI.
            visible_labels (Optional[int]): The number of visible labels for the question to be shown in the UI. \
                Setting it to None show all options.
            labels_order (Literal["natural", "suggestion"]): The order of the labels in the UI. \
                Can be either "natural" (order in which they were specified) or "suggestion" (order prioritizing those associated with a suggestion). \
                The score of the suggestion will be taken into account for ordering if available.
            title (Optional[str]: The title of the question to be shown in the UI.
            description (Optional[str]): The description of the question to be shown in the UI.
            required (bool): If the question is required for a record to be valid. At least one question must be required.
        """
        QuestionBase.__init__(
            self,
            name=name,
            title=title,
            required=required,
            description=description,
            settings=MultiLabelQuestionSettings(
                options=self._render_values_as_options(labels),
                visible_options=visible_labels,
                options_order=labels_order,
            ),
            _client=client,
        )

    @classmethod
    def from_model(cls, model: QuestionModel) -> "Self":
        instance = cls(name=model.name, labels=cls._render_options_as_labels(model.settings.options))  # noqa
        instance._model = model

        return instance


class TextQuestion(QuestionBase):
    def __init__(
        self,
        name: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        required: bool = True,
        use_markdown: bool = False,
        client: Optional[Argilla] = None,
    ) -> None:
        """Create a new text question for `Settings` of a `Dataset`. A text question \
            is a question where the user can input text.

        Parameters:
            name (str): The name of the question to be used as a reference.
            title (Optional[str]): The title of the question to be shown in the UI.
            description (Optional[str]): The description of the question to be shown in the UI.
            required (bool): If the question is required for a record to be valid. At least one question must be required.
            use_markdown (Optional[bool]): Whether to render the markdown in the UI. When True, you will be able \
                to use all the Markdown features for text formatting, including LaTex formulas and embedding multimedia content and PDFs.
        """
        super().__init__(
            name=name,
            title=title,
            required=required,
            description=description,
            settings=TextQuestionSettings(use_markdown=use_markdown),
            _client=client,
        )

    @property
    def use_markdown(self) -> bool:
        return self._model.settings.use_markdown

    @use_markdown.setter
    def use_markdown(self, use_markdown: bool) -> None:
        self._model.settings.use_markdown = use_markdown


class RatingQuestion(QuestionBase):
    def __init__(
        self,
        name: str,
        values: List[int],
        title: Optional[str] = None,
        description: Optional[str] = None,
        required: bool = True,
        client: Optional[Argilla] = None,
    ) -> None:
        """Create a new rating question for `Settings` of a `Dataset`. A rating question \
            is a question where the user can select a value from a sequential list of options.

        Parameters:
            name (str): The name of the question to be used as a reference.
            values (List[int]): The list of selectable values. It should be defined in the range [0, 10].
            title (Optional[str]:) The title of the question to be shown in the UI.
            description (Optional[str]): The description of the question to be shown in the UI.
            required (bool): If the question is required for a record to be valid. At least one question must be required.
        """

        super().__init__(
            name=name,
            title=title,
            required=required,
            description=description,
            settings=RatingQuestionSettings(options=self._render_values_as_options(values)),
            _client=client,
        )

    @property
    def values(self) -> List[int]:
        return self._render_options_as_labels(self._model.settings.options)  # noqa

    @values.setter
    def values(self, values: List[int]) -> None:
        self._model.values = self._render_values_as_options(values)

    @classmethod
    def from_model(cls, model: QuestionModel) -> "Self":
        instance = cls(name=model.name, values=cls._render_options_as_labels(model.settings.options))  # noqa
        instance._model = model

        return instance


class RankingQuestion(QuestionBase):
    def __init__(
        self,
        name: str,
        values: Union[List[str], Dict[str, str]],
        title: Optional[str] = None,
        description: Optional[str] = None,
        required: bool = True,
        client: Optional[Argilla] = None,
    ) -> None:
        """Create a new ranking question for `Settings` of a `Dataset`. A ranking question \
            is a question where the user can rank a list of options.

        Parameters:
            name (str): The name of the question to be used as a reference.
            values (Union[List[str], Dict[str, str]]): The list of options to be ranked, or a \
                dictionary of key-value pairs where the key is the label and the value is the label name displayed in the UI.
            title (Optional[str]:) The title of the question to be shown in the UI.
            description (Optional[str]): The description of the question to be shown in the UI.
            required (bool): If the question is required for a record to be valid. At least one question must be required.
        """
        super().__init__(
            name=name,
            title=title,
            required=required,
            description=description,
            settings=RankingQuestionSettings(options=self._render_values_as_options(values)),
            _client=client,
        )

    @property
    def values(self) -> List[str]:
        return self._render_options_as_labels(self._model.settings.options)

    @values.setter
    def values(self, values: List[int]) -> None:
        self._model.settings.options = self._render_values_as_options(values)

    @classmethod
    def from_model(cls, model: QuestionModel) -> "Self":
        instance = cls(name=model.name, values=cls._render_options_as_labels(model.settings.options))  # noqa
        instance._model = model

        return instance


class SpanQuestion(QuestionBase):
    def __init__(
        self,
        name: str,
        field: str,
        labels: Union[List[str], Dict[str, str]],
        allow_overlapping: bool = False,
        visible_labels: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        required: bool = True,
        client: Optional[Argilla] = None,
    ):
        """ Create a new span question for `Settings` of a `Dataset`. A span question \
            is a question where the user can select a section of text within a text field \
            and assign it a label.

            Parameters:
                name (str): The name of the question to be used as a reference.
                field (str): The name of the text field where the span question will be applied.
                labels (Union[List[str], Dict[str, str]]): The list of available labels for the question, or a \
                    dictionary of key-value pairs where the key is the label and the value is the label name displayed in the UI.
                allow_overlapping (bool): This value specifies whether overlapped spans are allowed or not.
                visible_labels (Optional[int]): The number of visible labels for the question to be shown in the UI. \
                    Setting it to None show all options.
                title (Optional[str]:) The title of the question to be shown in the UI.
                description (Optional[str]): The description of the question to be shown in the UI.
                required (bool): If the question is required for a record to be valid. At least one question must be required.
            """
        super().__init__(
            name=name,
            title=title,
            required=required,
            description=description,
            settings=SpanQuestionSettings(
                field=field,
                allow_overlapping=allow_overlapping,
                visible_options=visible_labels,
                options=self._render_values_as_options(labels),
            ),
            _client=client,
        )

    @property
    def field(self):
        return self._model.settings.field

    @field.setter
    def field(self, field: str):
        self._model.settings.field = field

    @property
    def allow_overlapping(self):
        return self._model.settings.allow_overlapping

    @allow_overlapping.setter
    def allow_overlapping(self, allow_overlapping: bool):
        self._model.settings.allow_overlapping = allow_overlapping

    @property
    def visible_labels(self) -> Optional[int]:
        return self._model.settings.visible_options

    @visible_labels.setter
    def visible_labels(self, visible_labels: Optional[int]) -> None:
        self._model.settings.visible_options = visible_labels

    @property
    def labels(self) -> List[str]:
        return self._render_options_as_labels(self._model.settings.options)

    @labels.setter
    def labels(self, labels: List[str]) -> None:
        self._model.settings.options = self._render_values_as_options(labels)

    @classmethod
    def from_model(cls, model: QuestionModel) -> "Self":
        instance = cls(
            name=model.name,
            field=model.settings.field,
            labels=cls._render_options_as_labels(model.settings.options),
        )  # noqa
        instance._model = model

        return instance


QuestionType = Union[
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    TextQuestion,
    RatingQuestion,
    SpanQuestion,
]


def question_from_model(model: QuestionModel) -> QuestionType:
    question_type = model.type

    if question_type == "label_selection":
        return LabelQuestion.from_model(model)
    elif question_type == "multi_label_selection":
        return MultiLabelQuestion.from_model(model)
    elif question_type == "ranking":
        return RankingQuestion.from_model(model)
    elif question_type == "text":
        return TextQuestion.from_model(model)
    elif question_type == "rating":
        return RatingQuestion.from_model(model)
    elif question_type == "span":
        return SpanQuestion.from_model(model)
    else:
        raise ValueError(f"Unsupported question model type: {question_type}")


def _question_from_dict(data: dict) -> QuestionType:
    return question_from_model(QuestionModel(**data))
