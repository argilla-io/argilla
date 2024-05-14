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

from typing import Union

from argilla_server.enums import QuestionType, ResponseStatus
from argilla_server.models import Record
from argilla_server.schemas.v1.responses import ResponseCreate, ResponseUpdate, ResponseUpsert
from argilla_server.validators.response_values import ResponseValueValidator


class ResponseValidator:
    def __init__(self, response_change: Union[ResponseCreate, ResponseUpdate, ResponseUpsert]):
        self._response_change = response_change

    def validate_for(self, record: Record) -> None:
        self._validate_values_are_present_when_submitted()
        self._validate_required_questions_have_values(record)
        self._validate_values_have_configured_questions(record)
        self._validate_values(record)

    @property
    def _is_submitted_response(self) -> bool:
        return self._response_change.status == ResponseStatus.submitted

    def _validate_values_are_present_when_submitted(self) -> None:
        if self._is_submitted_response and not self._response_change.values:
            raise ValueError("missing response values for submitted response")

    def _validate_required_questions_have_values(self, record: Record) -> None:
        for question in record.dataset.questions:
            if self._is_submitted_response and question.required and question.name not in self._response_change.values:
                raise ValueError(f"missing response value for required question with name={question.name!r}")

    def _validate_values_have_configured_questions(self, record: Record) -> None:
        question_names = [question.name for question in record.dataset.questions]

        for value_question_name in self._response_change.values or []:
            if value_question_name not in question_names:
                raise ValueError(f"found response value for non configured question with name={value_question_name!r}")

    def _validate_values(self, record: Record) -> None:
        if not self._response_change.values:
            return

        for question in record.dataset.questions:
            if question_response := self._response_change.values.get(question.name):
                ResponseValueValidator(question_response.value).validate_for(
                    question.parsed_settings,
                    record,
                    self._response_change.status,
                )


class ResponseCreateValidator(ResponseValidator):
    def __init__(self, response_create: ResponseCreate):
        self._response_change = response_create


class ResponseUpdateValidator(ResponseValidator):
    def __init__(self, response_update: ResponseUpdate):
        self._response_change = response_update


class ResponseUpsertValidator(ResponseValidator):
    def __init__(self, response_upsert: ResponseUpsert):
        self._response_change = response_upsert
