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

import argilla_sdk as rg
from argilla_sdk._models import TextFieldModel


class TestFieldsAPI:
    def test_create_many_fields(self, httpx_mock: HTTPXMock):
        # TODO: Add a test for the delete method in client
        mock_dataset_id = uuid.uuid4()
        mock_return_value = {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "string",
            "title": "string",
            "required": True,
            "settings": {"type": "text", "use_markdown": False},
            "dataset_id": str(mock_dataset_id),
            "inserted_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        mock_field = {
            "name": "5044cv0wu5",
            "title": "string",
            "required": True,
            "settings": {"type": "text", "use_markdown": False},
        }
        mock_field = TextFieldModel(**mock_field)
        httpx_mock.add_response(
            json=mock_return_value,
            url=f"http://test_url/api/v1/datasets/{mock_dataset_id}/fields",
            method="POST",
            status_code=200,
        )
        with httpx.Client() as client:
            client = rg.Argilla(api_url="http://test_url")
            client.api.fields.create_many(dataset_id=mock_dataset_id, fields=[mock_field])
