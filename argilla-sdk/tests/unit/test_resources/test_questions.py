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

import uuid
from datetime import datetime

import httpx
from pytest_httpx import HTTPXMock

import argilla as rg
from argilla._models import TextQuestionModel, LabelQuestionModel
from argilla._models._settings._questions import SpanQuestionModel


class TestQuestionsAPI:
    def test_create_many_questions(self, httpx_mock: HTTPXMock):
        # TODO: Add a test for the delete method in client
        mock_dataset_id = uuid.uuid4()
        mock_return_value = {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "string",
            "title": "string",
            "required": True,
            "settings": {"type": "text", "use_markdown": False},
            "dataset_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "inserted_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        mock_question = {
            "name": "5044cv0wu5",
            "title": "string",
            "description": "string",
            "required": True,
            "settings": {"type": "text", "use_markdown": False},
        }
        mock_question = TextQuestionModel(**mock_question)
        httpx_mock.add_response(
            json=mock_return_value,
            url=f"http://test_url/api/v1/datasets/{mock_dataset_id}/questions",
            method="POST",
            status_code=200,
        )
        with httpx.Client() as client:
            client = rg.Argilla(api_url="http://test_url")
            client.api.questions.create_many(dataset_id=mock_dataset_id, questions=[mock_question])

    def test_create_many_label_questions(self, httpx_mock: HTTPXMock):
        # TODO: Add a test for the delete method in client
        mock_dataset_id = uuid.uuid4()
        mock_return_value = {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "string",
            "title": "string",
            "required": True,
            "settings": {"type": "labels", "options": [{"text": "positive", "value": "positive"}]},
            "dataset_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "inserted_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        mock_question = {
            "name": "5044cv0wu5",
            "title": "string",
            "description": "string",
            "required": True,
            "settings": {
                "type": "label",
                "options": [{"text": "negative", "value": "negative"}, {"text": "positive", "value": "positive"}],
            },
        }
        mock_question = LabelQuestionModel(**mock_question)
        httpx_mock.add_response(
            json=mock_return_value,
            url=f"http://test_url/api/v1/datasets/{mock_dataset_id}/questions",
            method="POST",
            status_code=200,
        )
        with httpx.Client() as client:
            client = rg.Argilla(api_url="http://test_url")
            client.api.questions.create_many(dataset_id=mock_dataset_id, questions=[mock_question])

    def test_create_span_question(self, httpx_mock: HTTPXMock):
        mock_dataset_id = uuid.uuid4()
        mock_return_value = {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "string",
            "title": "string",
            "required": True,
            "settings": {
                "type": "span",
                "allow_overlapping": True,
                "field": "text",
                "visible_options": 3,
                "options": [
                    {"value": "value 1", "text": "Value 1"},
                    {"value": "value 2", "text": "Value 2"},
                    {"value": "value 3", "text": "Value 3"},
                ],
            },
            "inserted_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        httpx_mock.add_response(
            json=mock_return_value,
            url=f"http://test_url/api/v1/datasets/{mock_dataset_id}/questions",
            method="POST",
            status_code=200,
        )

        with httpx.Client() as _:
            question = SpanQuestionModel(
                name="5044cv0wu5",
                title="string",
                description="string",
                required=True,
                settings={
                    "type": "span",
                    "allow_overlapping": True,
                    "field": "text",
                    "visible_options": 3,
                    "options": [
                        {"value": "value 1", "text": "Value 1"},
                        {"value": "value 2", "text": "Value 2"},
                        {"value": "value 3", "text": "Value 3"},
                    ],
                },
            )

            client = rg.Argilla(api_url="http://test_url")
            created_question = client.api.questions.create(dataset_id=mock_dataset_id, question=question)
            assert created_question.model_dump(exclude_unset=True) == mock_return_value
