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

from typing import List, Dict
from uuid import UUID

import httpx
from argilla._api._base import ResourceAPI
from argilla._exceptions import api_error_handler
from argilla._models import QuestionModel

__all__ = ["QuestionsAPI"]


class QuestionsAPI(ResourceAPI[QuestionModel]):
    """Manage datasets via the API"""

    http_client: httpx.Client

    ################
    # CRUD methods #
    ################

    @api_error_handler
    def create(
        self,
        question: QuestionModel,
    ) -> QuestionModel:
        url = f"/api/v1/datasets/{question.dataset_id}/questions"
        response = self.http_client.post(url=url, json=question.model_dump())
        response.raise_for_status()
        response_json = response.json()
        question_model = self._model_from_json(response_json=response_json)
        self._log_message(message=f"Created question {question_model.name} in dataset {question.dataset_id}")
        return question_model

    @api_error_handler
    def update(
        self,
        question: QuestionModel,
    ) -> QuestionModel:
        url = f"/api/v1/questions/{question.id}"
        response = self.http_client.patch(url, json=question.model_dump())
        response.raise_for_status()
        response_json = response.json()
        updated_question = self._model_from_json(response_json)
        self._log_message(message=f"Update question {updated_question.name} with id {question.id}")
        return updated_question

    @api_error_handler
    def delete(self, question_id: UUID) -> None:
        url = f"/api/v1/questions/{question_id}"
        self.http_client.delete(url).raise_for_status()
        self._log_message(message=f"Deleted question with id {question_id}")

    ####################
    # Utility methods #
    ####################

    @api_error_handler
    def list(self, dataset_id: UUID) -> List[QuestionModel]:
        response = self.http_client.get(f"/api/v1/datasets/{dataset_id}/questions")
        response.raise_for_status()
        response_json = response.json()
        response_models = self._model_from_jsons(response_jsons=response_json["items"])
        return response_models

    ####################
    # Private methods #
    ####################

    def _model_from_json(self, response_json: Dict) -> QuestionModel:
        return QuestionModel(**response_json)

    def _model_from_jsons(self, response_jsons: List[Dict]) -> List[QuestionModel]:
        return list(map(self._model_from_json, response_jsons))
