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
from argilla._models import FieldModel
from argilla._models._settings._fields import ImageFieldSettings
from argilla.settings._field import ImageField


class TestImageField:
    def test_create_image_field_ony_with_required_arguments(self):
        field = ImageField(name="image")

        assert field.name == "image"
        assert field.title == "image"
        assert field.required is True
        assert field.description is None

    def test_create_image_field_from_dict(self):
        field = ImageField.from_dict(
            {
                "name": "image",
                "title": "Image title",
                "required": "false",
                "description": "Image description",
                "settings": {"type": "image"},
            }
        )

        assert field.name == "image"
        assert field.title == "Image title"
        assert field.description == "Image description"
        assert field.required is False
        assert isinstance(field._model.settings, ImageFieldSettings)


class TestFieldsAPI:
    def test_create_field(self, httpx_mock: HTTPXMock):
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
        mock_field = FieldModel(**mock_field, dataset_id=mock_dataset_id)
        httpx_mock.add_response(
            json=mock_return_value,
            url=f"http://test_url/api/v1/datasets/{mock_dataset_id}/fields",
            method="POST",
            status_code=200,
        )
        with httpx.Client() as client:
            client = rg.Argilla(api_url="http://test_url")
            client.api.fields.create(mock_field)
