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

import pytest
import uuid
from datetime import datetime
from tempfile import TemporaryDirectory

import httpx
from pytest_httpx import HTTPXMock

import argilla as rg


@pytest.fixture
def settings():
    settings = rg.Settings(
        fields=[
            rg.TextField(name="text", title="text"),
        ],
        metadata=[
            rg.FloatMetadataProperty("source"),
        ],
        questions=[
            rg.LabelQuestion(name="label", title="text", labels=["positive", "negative"]),
        ],
        vectors=[rg.VectorField(name="text_vector", dimensions=3)],
    )
    return settings


@pytest.fixture
def dataset(httpx_mock: HTTPXMock, settings) -> rg.Dataset:
    api_url = "http://test_url"
    client = rg.Argilla(api_url)
    workspace_id = uuid.uuid4()
    workspace_name = "workspace-01"
    mock_workspace = {
        "id": str(workspace_id),
        "name": workspace_name,
        "inserted_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    httpx_mock.add_response(
        json={"items": [mock_workspace]},
        url=f"{api_url}/api/v1/me/workspaces",
        method="GET",
        status_code=200,
    )

    httpx_mock.add_response(
        url=f"{api_url}/api/v1/workspaces/{workspace_id}",
        method="GET",
        status_code=200,
        json=mock_workspace,
    )

    with httpx.Client():
        dataset = rg.Dataset(
            client=client,
            name=f"dataset_{uuid.uuid4()}",
            settings=settings,
            workspace=workspace_name,
        )
        yield dataset


def test_settings_to_json(settings):
    with TemporaryDirectory() as temp_dir:
        temp_file_path = f"{temp_dir}/settings.json"
        settings.to_json(temp_file_path)
        with open(temp_file_path, "r") as f:
            settings_json = f.read()

            assert "fields" in settings_json
            assert "questions" in settings_json
            assert "metadata" in settings_json
            assert "vectors" in settings_json

        loaded_settings = rg.Settings.from_json(temp_file_path)
        assert settings == loaded_settings


def test_export_settings_from_disk(settings):
    with TemporaryDirectory() as temp_dir:
        temp_file_path = f"{temp_dir}/settings.json"
        settings.to_json(temp_file_path)
        loaded_settings = rg.Settings.from_json(temp_file_path)

    assert settings == loaded_settings
