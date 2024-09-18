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

from argilla_server.api.schemas.v1.questions import QuestionSettings
from argilla_server.api.schemas.v1.suggestions import SuggestionCreate
from argilla_server.errors.future import UnprocessableEntityError
from argilla_server.models.database import Record
from argilla_server.validators.response_values import ResponseValueValidator


class SuggestionCreateValidator:
    @classmethod
    def validate(cls, suggestion_create: SuggestionCreate, question_settings: QuestionSettings, record: Record) -> None:
        cls._validate_value(suggestion_create, question_settings, record)
        cls._validate_score(suggestion_create)

    @staticmethod
    def _validate_value(
        suggestion_create: SuggestionCreate, question_settings: QuestionSettings, record: Record
    ) -> None:
        ResponseValueValidator.validate(suggestion_create.value, question_settings, record)

    @classmethod
    def _validate_score(cls, suggestion_create: SuggestionCreate):
        cls._validate_value_and_score_cardinality(suggestion_create)
        cls._validate_value_and_score_have_same_length(suggestion_create)

    @staticmethod
    def _validate_value_and_score_cardinality(suggestion_create: SuggestionCreate):
        if not isinstance(suggestion_create.value, list) and isinstance(suggestion_create.score, list):
            raise UnprocessableEntityError("a list of score values is not allowed for a suggestion with a single value")

        if (
            isinstance(suggestion_create.value, list)
            and suggestion_create.score is not None
            and not isinstance(suggestion_create.score, list)
        ):
            raise UnprocessableEntityError(
                "a single score value is not allowed for a suggestion with a multiple items value"
            )

    @staticmethod
    def _validate_value_and_score_have_same_length(suggestion_create: SuggestionCreate) -> None:
        if not isinstance(suggestion_create.value, list) or not isinstance(suggestion_create.score, list):
            return

        if len(suggestion_create.value) != len(suggestion_create.score):
            raise UnprocessableEntityError("number of items on value and score attributes doesn't match")
