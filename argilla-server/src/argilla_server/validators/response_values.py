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

from typing import Optional

from argilla_server.api.schemas.v1.questions import (
    LabelSelectionQuestionSettings,
    MultiLabelSelectionQuestionSettings,
    QuestionSettings,
    RankingQuestionSettings,
    RatingQuestionSettings,
    SpanQuestionSettings,
)
from argilla_server.api.schemas.v1.responses import (
    MultiLabelSelectionQuestionResponseValue,
    RankingQuestionResponseValue,
    RatingQuestionResponseValue,
    ResponseValueTypes,
    SpanQuestionResponseValue,
    TextAndLabelSelectionQuestionResponseValue,
)
from argilla_server.enums import QuestionType, ResponseStatus
from argilla_server.errors.future import UnprocessableEntityError
from argilla_server.models import Record


class ResponseValueValidator:
    @classmethod
    def validate(
        cls,
        response_value: ResponseValueTypes,
        question_settings: QuestionSettings,
        record: Record,
        response_status: Optional[ResponseStatus] = None,
    ) -> None:
        if question_settings.type == QuestionType.text:
            TextQuestionResponseValueValidator(response_value).validate()
        elif question_settings.type == QuestionType.label_selection:
            LabelSelectionQuestionResponseValueValidator(response_value).validate_for(question_settings)
        elif question_settings.type == QuestionType.multi_label_selection:
            MultiLabelSelectionQuestionResponseValueValidator(response_value).validate_for(question_settings)
        elif question_settings.type == QuestionType.rating:
            RatingQuestionResponseValueValidator(response_value).validate_for(question_settings)
        elif question_settings.type == QuestionType.ranking:
            RankingQuestionResponseValueValidator(response_value).validate_for(question_settings, response_status)
        elif question_settings.type == QuestionType.span:
            SpanQuestionResponseValueValidator(response_value).validate_for(question_settings, record)
        else:
            raise UnprocessableEntityError(f"unknown question type f{question_settings.type!r}")


class TextQuestionResponseValueValidator:
    def __init__(self, response_value: TextAndLabelSelectionQuestionResponseValue):
        self._response_value = response_value

    def validate(self) -> None:
        self._validate_value_type()

    def _validate_value_type(self) -> None:
        if not isinstance(self._response_value, str):
            raise UnprocessableEntityError(f"text question expects a text value, found {type(self._response_value)}")


class LabelSelectionQuestionResponseValueValidator:
    def __init__(self, response_value: TextAndLabelSelectionQuestionResponseValue):
        self._response_value = response_value

    def validate_for(self, label_selection_question_settings: LabelSelectionQuestionSettings) -> None:
        self._validate_label_is_available_at_question_settings(label_selection_question_settings)

    def _validate_label_is_available_at_question_settings(
        self, label_selection_question_settings: LabelSelectionQuestionSettings
    ) -> None:
        available_labels = [option.value for option in label_selection_question_settings.options]

        if self._response_value not in available_labels:
            raise UnprocessableEntityError(
                f"{self._response_value!r} is not a valid label for label selection question.\nValid labels are: {available_labels!r}"
            )


class MultiLabelSelectionQuestionResponseValueValidator:
    def __init__(self, response_value: MultiLabelSelectionQuestionResponseValue):
        self._response_value = response_value

    def validate_for(self, multi_label_selection_question_settings: MultiLabelSelectionQuestionSettings) -> None:
        self._validate_value_type()
        self._validate_labels_are_not_empty()
        self._validate_labels_are_unique()
        self._validate_labels_are_available_at_question_settings(multi_label_selection_question_settings)

    def _validate_value_type(self) -> None:
        if not isinstance(self._response_value, list):
            raise UnprocessableEntityError(
                f"multi label selection questions expects a list of values, found {type(self._response_value)}"
            )

    def _validate_labels_are_not_empty(self) -> None:
        if len(self._response_value) == 0:
            raise UnprocessableEntityError("multi label selection questions expects a list of values, found empty list")

    def _validate_labels_are_unique(self) -> None:
        if len(self._response_value) != len(set(self._response_value)):
            raise UnprocessableEntityError(
                "multi label selection questions expect a list of unique values, but duplicates were found"
            )

    def _validate_labels_are_available_at_question_settings(
        self, multi_label_selection_question_settings: MultiLabelSelectionQuestionSettings
    ) -> None:
        available_labels = [option.value for option in multi_label_selection_question_settings.options]
        invalid_labels = sorted(list(set(self._response_value) - set(available_labels)))

        if invalid_labels:
            raise UnprocessableEntityError(
                f"{invalid_labels!r} are not valid labels for multi label selection question.\nValid labels are: {available_labels!r}"
            )


class RatingQuestionResponseValueValidator:
    def __init__(self, response_value: RatingQuestionResponseValue):
        self._response_value = response_value

    def validate_for(self, rating_question_settings: RatingQuestionSettings) -> None:
        self._validate_rating_is_available_at_question_settings(rating_question_settings)

    def _validate_rating_is_available_at_question_settings(
        self, rating_question_settings: RatingQuestionSettings
    ) -> None:
        available_options = [option.value for option in rating_question_settings.options]

        if self._response_value not in available_options:
            raise UnprocessableEntityError(
                f"{self._response_value!r} is not a valid rating for rating question.\nValid ratings are: {available_options!r}"
            )


class RankingQuestionResponseValueValidator:
    def __init__(self, response_value: RankingQuestionResponseValue):
        self._response_value = response_value

    def validate_for(
        self, ranking_question_settings: RankingQuestionSettings, response_status: Optional[ResponseStatus] = None
    ) -> None:
        self._validate_value_type()
        self._validate_all_rankings_are_present_when_submitted(ranking_question_settings, response_status)
        self._validate_all_rankings_are_valid_when_submitted(ranking_question_settings, response_status)
        self._validate_values_are_available_at_question_settings(ranking_question_settings)
        self._validate_values_are_unique()

    def _validate_value_type(self) -> None:
        if not isinstance(self._response_value, list):
            raise UnprocessableEntityError(
                f"ranking question expects a list of values, found {type(self._response_value)}"
            )

    def _validate_all_rankings_are_present_when_submitted(
        self, ranking_question_settings: RankingQuestionSettings, response_status: Optional[ResponseStatus] = None
    ) -> None:
        if response_status != ResponseStatus.submitted:
            return

        available_values = [option.value for option in ranking_question_settings.options]
        available_values_len = len(available_values)

        if len(self._response_value) != available_values_len:
            raise UnprocessableEntityError(
                f"ranking question expects a list containing {available_values_len} values, found a list of {len(self._response_value)} values"
            )

    def _validate_all_rankings_are_valid_when_submitted(
        self,
        ranking_question_settings: RankingQuestionSettings,
        response_status: Optional[ResponseStatus] = None,
    ) -> None:
        if response_status != ResponseStatus.submitted:
            return

        available_rankings = list(range(1, len(ranking_question_settings.options) + 1))
        response_rankings = [value_item.rank for value_item in self._response_value]
        invalid_rankings = sorted(list(set(response_rankings) - set(available_rankings)))

        if invalid_rankings:
            raise UnprocessableEntityError(
                f"{invalid_rankings!r} are not valid ranks for ranking question.\nValid ranks are: {available_rankings!r}"
            )

    def _validate_values_are_available_at_question_settings(
        self, ranking_question_settings: RankingQuestionSettings
    ) -> None:
        available_values = [option.value for option in ranking_question_settings.options]
        response_values = [value_item.value for value_item in self._response_value]
        invalid_values = sorted(list(set(response_values) - set(available_values)))

        if invalid_values:
            raise UnprocessableEntityError(
                f"{invalid_values!r} are not valid values for ranking question.\nValid values are: {available_values!r}"
            )

    def _validate_values_are_unique(self) -> None:
        response_values = [value_item.value for value_item in self._response_value]

        if len(response_values) != len(set(response_values)):
            raise UnprocessableEntityError(
                "ranking question expects a list of unique values, but duplicates were found"
            )


class SpanQuestionResponseValueValidator:
    def __init__(self, response_value: SpanQuestionResponseValue):
        self._response_value = response_value

    def validate_for(self, span_question_settings: SpanQuestionSettings, record: Record) -> None:
        self._validate_value_type()
        self._validate_question_settings_field_is_present_at_record(span_question_settings, record)
        self._validate_start_end_are_within_record_field_limits(span_question_settings, record)
        self._validate_labels_are_available_at_question_settings(span_question_settings)
        self._validate_values_are_not_overlapped(span_question_settings)

    def _validate_value_type(self) -> None:
        if not isinstance(self._response_value, list):
            raise UnprocessableEntityError(
                f"span question expects a list of values, found {type(self._response_value)}"
            )

    def _validate_question_settings_field_is_present_at_record(
        self, span_question_settings: SpanQuestionSettings, record: Record
    ) -> None:
        if span_question_settings.field not in record.fields:
            raise UnprocessableEntityError(
                f"span question requires record to have field `{span_question_settings.field}`"
            )

    def _validate_start_end_are_within_record_field_limits(
        self, span_question_settings: SpanQuestionSettings, record: Record
    ) -> None:
        field_len = len(record.fields[span_question_settings.field])

        for value_item in self._response_value:
            if value_item.start > (field_len - 1):
                raise UnprocessableEntityError(
                    f"span question response value `start` must have a value lower than record field `{span_question_settings.field}` length that is `{field_len}`"
                )

            if value_item.end > field_len:
                raise UnprocessableEntityError(
                    f"span question response value `end` must have a value lower or equal than record field `{span_question_settings.field}` length that is `{field_len}`"
                )

    def _validate_labels_are_available_at_question_settings(self, span_question_settings: SpanQuestionSettings) -> None:
        available_labels = [option.value for option in span_question_settings.options]

        for value_item in self._response_value:
            if value_item.label not in available_labels:
                raise UnprocessableEntityError(
                    f"undefined label '{value_item.label}' for span question.\nValid labels are: {available_labels!r}"
                )

    def _validate_values_are_not_overlapped(self, span_question_settings: SpanQuestionSettings) -> None:
        if span_question_settings.allow_overlapping:
            return

        for span_i, value_item in enumerate(self._response_value):
            for span_j, other_value_item in enumerate(self._response_value):
                if (
                    span_i != span_j
                    and value_item.start < other_value_item.end
                    and value_item.end > other_value_item.start
                ):
                    raise UnprocessableEntityError(
                        f"overlapping values found between spans at index idx={span_i} and idx={span_j}"
                    )
