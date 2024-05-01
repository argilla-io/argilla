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

from argilla_server.models.database import Record
from argilla_server.schemas.v1.questions import QuestionSettings
from argilla_server.schemas.v1.suggestions import SuggestionCreate
from argilla_server.validators.response_values import ResponseValueValidator


class SuggestionCreateValidator:
    def __init__(self, suggestion_create: SuggestionCreate):
        self._suggestion_create = suggestion_create

    def validate_for(self, question_settings: QuestionSettings, record: Record) -> None:
        self._validate_value(question_settings, record)
        self._validate_score()

    def _validate_value(self, question_settings: QuestionSettings, record: Record) -> None:
        ResponseValueValidator(self._suggestion_create.value).validate_for(question_settings, record)

    def _validate_score(self):
        self._validate_value_and_score_cardinality()
        self._validate_value_and_score_have_same_length()

    def _validate_value_and_score_cardinality(self):
        if not isinstance(self._suggestion_create.value, list) and isinstance(self._suggestion_create.score, list):
            raise ValueError("a list of score values is not allowed for a suggestion with a single value")

        if (
            isinstance(self._suggestion_create.value, list)
            and self._suggestion_create.score is not None
            and not isinstance(self._suggestion_create.score, list)
        ):
            raise ValueError("a single score value is not allowed for a suggestion with a multiple items value")

    def _validate_value_and_score_have_same_length(self) -> None:
        if not isinstance(self._suggestion_create.value, list) or not isinstance(self._suggestion_create.score, list):
            return

        if len(self._suggestion_create.value) != len(self._suggestion_create.score):
            raise ValueError("number of items on value and score attributes doesn't match")
