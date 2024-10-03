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
from argilla._models import (
    TextQuestionModel,
    LabelQuestionModel,
    MultiLabelQuestionModel,
    RankingQuestionModel,
    RatingQuestionModel,
    SpanQuestionModel,
    QuestionBaseModel,
    QuestionModel,
)

__all__ = ["QuestionsAPI"]


class QuestionsAPI(ResourceAPI[QuestionBaseModel]):
    """Manage datasets via the API"""

    http_client: httpx.Client

    _TYPE_TO_MODEL_CLASS = {
        "text": TextQuestionModel,
        "label_selection": LabelQuestionModel,
        "multi_label_selection": MultiLabelQuestionModel,
        "ranking": RankingQuestionModel,
        "rating": RatingQuestionModel,
        "span": SpanQuestionModel,
    }

    ################
    # CRUD methods #
    ################

    @api_error_handler
    def create(
        self,
        dataset_id: UUID,
        question: QuestionModel,
    ) -> QuestionModel:
        url = f"/api/v1/datasets/{dataset_id}/questions"
        response = self.http_client.post(url=url, json=question.model_dump())
        response.raise_for_status()
        response_json = response.json()
        question_model = self._model_from_json(response_json=response_json)
        self._log_message(message=f"Created question {question_model.name} in dataset {dataset_id}")
        return question_model

    @api_error_handler
    def update(
        self,
        question: QuestionModel,
    ) -> QuestionModel:
        # TODO: Implement update method for fields with server side ID
        return question

    @api_error_handler
    def delete(self, question_id: UUID) -> None:
        # TODO: Implement delete method for fields with server side ID
        pass

    ####################
    # Utility methods #
    ####################

    def create_many(self, dataset_id: UUID, questions: List[QuestionModel]) -> List[QuestionModel]:
        response_models = []
        for question in questions:
            response_model = self.create(dataset_id=dataset_id, question=question)
            response_models.append(response_model)
        return response_models

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
        response_json["inserted_at"] = self._date_from_iso_format(date=response_json["inserted_at"])
        response_json["updated_at"] = self._date_from_iso_format(date=response_json["updated_at"])
        return self._get_model_from_response(response_json=response_json)

    def _model_from_jsons(self, response_jsons: List[Dict]) -> List[QuestionModel]:
        return list(map(self._model_from_json, response_jsons))

    def _get_model_from_response(self, response_json: Dict) -> QuestionModel:
        """Get the model from the response"""
        try:
            question_type = response_json.get("settings", {}).get("type")
        except Exception as e:
            raise ValueError("Invalid field type: missing 'settings.type' in response") from e

        question_class = self._TYPE_TO_MODEL_CLASS.get(question_type)
        if question_class is None:
            self._log_message(message=f"Unknown question type: {question_type}")
            question_class = QuestionBaseModel

        return question_class(**response_json, check_fields=False)
