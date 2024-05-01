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

from typing import List

from argilla_server.enums import QuestionType
from argilla_server.models.database import Dataset, Question
from argilla_server.schemas.v1.questions import (
    QuestionCreate,
    QuestionSettings,
    QuestionSettingsUpdate,
    QuestionUpdate,
    SpanQuestionSettings,
)


class InvalidQuestionSettings(Exception):
    pass


class QuestionCreateValidator:
    def __init__(self, question_create: QuestionCreate):
        self._question_create = question_create

    def validate_for(self, dataset: Dataset):
        self._validate_dataset_is_not_ready(dataset)
        self._validate_span_question_settings(dataset)

    def _validate_dataset_is_not_ready(self, dataset):
        if dataset.is_ready:
            raise ValueError("questions cannot be created for a published dataset")

    def _validate_span_question_settings(self, dataset: Dataset):
        if self._question_create.settings.type != QuestionType.span:
            return

        field = self._question_create.settings.field
        field_names = [field.name for field in dataset.fields]

        if field not in field_names:
            raise ValueError(f"'{field}' is not a valid field name.\nValid field names are {field_names!r}")

        for question in dataset.questions:
            if question.type == QuestionType.span and field == question.parsed_settings.field:
                raise ValueError(f"'{field}' is already used by span question with id '{question.id}'")


class QuestionUpdateValidator:
    QUESTION_TYPES_WITH_LABEL_OPTIONS = [
        QuestionType.label_selection,
        QuestionType.multi_label_selection,
        QuestionType.span,
    ]

    QUESTION_TYPES_WITH_VISIBLE_OPTIONS = [
        QuestionType.label_selection,
        QuestionType.multi_label_selection,
        QuestionType.span,
    ]

    def __init__(self, question_update: QuestionUpdate):
        self._question_update = question_update

    def validate_for(self, question: Question):
        self._validate_question_settings(question.parsed_settings)

    def _validate_question_settings(self, question_settings: QuestionSettings):
        if not self._question_update.settings:
            return

        self._validate_question_settings_type_is_the_same(question_settings, self._question_update.settings)
        self._validate_question_settings_label_options(question_settings, self._question_update.settings)
        self._validate_question_settings_visible_options(question_settings, self._question_update.settings)
        self._validate_span_question_settings(question_settings, self._question_update.settings)

    def _validate_question_settings_type_is_the_same(
        self, question_settings: QuestionSettings, question_settings_update: QuestionSettingsUpdate
    ):
        if question_settings.type != question_settings_update.type:
            raise InvalidQuestionSettings(
                f"question type cannot be changed. expected '{question_settings.type}' but got '{question_settings_update.type}'"
            )

    def _validate_question_settings_label_options(
        self, question_settings: QuestionSettings, question_settings_update: QuestionSettingsUpdate
    ):
        if question_settings.type not in self.QUESTION_TYPES_WITH_LABEL_OPTIONS:
            return

        if question_settings_update.options is None:
            return

        if len(question_settings.options) != len(question_settings_update.options):
            raise InvalidQuestionSettings(
                f"the number of options cannot be modified. expected {len(question_settings.options)} but got {len(question_settings_update.options)}"
            )

        sorted_options = sorted(question_settings.options, key=lambda option: option.value)
        sorted_update_options = sorted(question_settings_update.options, key=lambda option: option.value)

        unexpected_options: List[str] = []
        for option, update_option in zip(sorted_options, sorted_update_options):
            if option.value != update_option.value:
                unexpected_options.append(update_option.value)

        if unexpected_options:
            raise InvalidQuestionSettings(
                f"the option values cannot be modified. found unexpected option values: {unexpected_options!r}"
            )

    def _validate_question_settings_visible_options(
        self, question_settings: QuestionSettings, question_settings_update: QuestionSettingsUpdate
    ):
        if question_settings_update.type not in self.QUESTION_TYPES_WITH_VISIBLE_OPTIONS:
            return

        if question_settings_update.visible_options is None:
            return

        number_of_options = len(question_settings.options)
        if question_settings_update.visible_options > number_of_options:
            raise InvalidQuestionSettings(
                f"the value for 'visible_options' must be less or equal to the number of items in 'options' ({number_of_options})"
            )

    def _validate_span_question_settings(
        self, question_settings: SpanQuestionSettings, question_settings_update: QuestionSettingsUpdate
    ) -> None:
        if question_settings_update.type != QuestionType.span:
            return

        if question_settings.allow_overlapping and not question_settings_update.allow_overlapping:
            raise InvalidQuestionSettings(
                "'allow_overlapping' can't be disabled because responses may become inconsistent"
            )


class QuestionDeleteValidator:
    def validate_for(self, dataset: Dataset):
        self._validate_dataset_is_not_ready(dataset)

    def _validate_dataset_is_not_ready(self, dataset):
        if dataset.is_ready:
            raise ValueError("questions cannot be deleted for a published dataset")
