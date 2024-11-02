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

from typing import Union, TypeAlias

from argilla_server.api.schemas.v1.responses import ResponseCreate, ResponseUpdate, ResponseUpsert
from argilla_server.enums import ResponseStatus
from argilla_server.errors.future import UnprocessableEntityError
from argilla_server.models import Record
from argilla_server.validators.response_values import ResponseValueValidator


def _is_submitted_response(response: Union[ResponseCreate, ResponseUpdate, ResponseUpsert]) -> bool:
    return response.status == ResponseStatus.submitted


class ResponseValidator:
    @classmethod
    def validate(cls, response: Union[ResponseCreate, ResponseUpdate, ResponseUpsert], record: Record) -> None:
        cls._validate_values_are_present_when_submitted(response)
        cls._validate_required_questions_have_values(response, record)
        cls._validate_values_have_configured_questions(response, record)
        cls._validate_values(response, record)

    @staticmethod
    def _validate_values_are_present_when_submitted(
        response: Union[ResponseCreate, ResponseUpdate, ResponseUpsert],
    ) -> None:
        if _is_submitted_response(response) and not response.values:
            raise UnprocessableEntityError("missing response values for submitted response")

    @staticmethod
    def _validate_required_questions_have_values(
        response: Union[ResponseCreate, ResponseUpdate, ResponseUpsert], record: Record
    ) -> None:
        for question in record.dataset.questions:
            if _is_submitted_response(response) and question.required and question.name not in response.values:
                raise UnprocessableEntityError(
                    f"missing response value for required question with name={question.name!r}"
                )

    @staticmethod
    def _validate_values_have_configured_questions(
        response: Union[ResponseCreate, ResponseUpdate, ResponseUpsert], record: Record
    ) -> None:
        question_names = [question.name for question in record.dataset.questions]

        for value_question_name in response.values or []:
            if value_question_name not in question_names:
                raise UnprocessableEntityError(
                    f"found response value for non configured question with name={value_question_name!r}"
                )

    @staticmethod
    def _validate_values(response: Union[ResponseCreate, ResponseUpdate, ResponseUpsert], record: Record) -> None:
        if not response.values:
            return

        for question in record.dataset.questions:
            if question_response := response.values.get(question.name):
                ResponseValueValidator.validate(
                    question_response.value,
                    question.parsed_settings,
                    record,
                    response.status,
                )


ResponseCreateValidator: TypeAlias = ResponseValidator
ResponseUpdateValidator: TypeAlias = ResponseValidator
ResponseUpsertValidator: TypeAlias = ResponseValidator
