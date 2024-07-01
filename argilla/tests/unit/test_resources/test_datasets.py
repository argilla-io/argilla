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
import pytest
from pytest_httpx import HTTPXMock

import argilla as rg
from argilla._exceptions import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    UnprocessableEntityError,
)


@pytest.fixture
def dataset(httpx_mock: HTTPXMock) -> rg.Dataset:
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
            settings=rg.Settings(
                fields=[
                    rg.TextField(name="text"),
                ],
                questions=[
                    rg.TextQuestion(name="response"),
                ],
            ),
            workspace=workspace_name,
        )
        yield dataset


@pytest.mark.skip(reason="HTTP mocked calls must be updated")
class TestDatasets:
    def url(self, path: str) -> str:
        return f"http://test_url{path}"

    @pytest.mark.parametrize(
        "status_code, expected_exception, expected_message",
        [
            (200, None, None),
            (400, BadRequestError, "BadRequestError"),
            (403, ForbiddenError, "ForbiddenError"),
            (404, NotFoundError, "NotFoundError"),
            (409, ConflictError, "ConflictError"),
            (422, UnprocessableEntityError, "UnprocessableEntityError"),
            (500, InternalServerError, "InternalServerError"),
        ],
    )
    def test_create_dataset(self, httpx_mock: HTTPXMock, status_code, expected_exception, expected_message, dataset):
        mock_dataset_id = uuid.uuid4()
        mock_return_value = {
            "id": str(mock_dataset_id),
            "name": "dataset-01",
            "status": "draft",
            "allow_extra_metadata": False,
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        httpx_mock.add_response(
            json=mock_return_value,
            url=self.url("/api/v1/datasets"),
            method="POST",
            status_code=status_code,
        )

        if status_code == 200:
            httpx_mock.add_response(
                json=mock_return_value,
                url=self.url(f"/api/v1/datasets/{mock_dataset_id}"),
                method="GET",
                status_code=200,
            )
            httpx_mock.add_response(
                json=mock_return_value,
                url=self.url(f"/api/v1/datasets/{mock_dataset_id}/publish"),
                method="PUT",
                status_code=200,
            )
            self._mock_dataset_settings(httpx_mock, mock_dataset_id, mock_return_value)
        with httpx.Client():
            if expected_exception:
                with pytest.raises(expected_exception=expected_exception) as excinfo:
                    dataset.create()
                assert expected_message in str(excinfo.value)
            else:
                dataset.create()
                assert dataset.name == mock_return_value["name"]

    @pytest.mark.parametrize(
        "status_code, expected_exception, expected_message",
        [
            (200, None, None),
            (400, BadRequestError, "BadRequestError"),
            (403, ForbiddenError, "ForbiddenError"),
            (404, NotFoundError, "NotFoundError"),
            (409, ConflictError, "ConflictError"),
            (422, UnprocessableEntityError, "UnprocessableEntityError"),
            (500, InternalServerError, "InternalServerError"),
        ],
    )
    def test_update_dataset(self, httpx_mock: HTTPXMock, status_code, expected_exception, expected_message, dataset):
        mock_dataset_id = uuid.uuid4()
        mock_workspace_id = uuid.uuid4()
        mock_patch_return_value = {
            "id": str(mock_dataset_id),
            "name": "new_name",
            "workspace_id": str(mock_workspace_id),
            "guidelines": "guidelines",
            "allow_extra_metadata": False,
            "last_activity_at": datetime.utcnow().isoformat(),
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        httpx_mock.add_response(
            json=mock_patch_return_value,
            url=self.url(f"/api/v1/datasets/{mock_dataset_id}"),
            method="GET",
            status_code=200,
        )
        httpx_mock.add_response(
            json=mock_patch_return_value,
            url=self.url(f"/api/v1/datasets/{mock_dataset_id}"),
            method="PATCH",
            status_code=status_code,
        )

        dataset.id = mock_dataset_id
        if status_code == 200:
            httpx_mock.add_response(
                json={
                    "id": str(uuid.uuid4()),
                    "name": "text",
                    "settings": {"type": "text", "use_markdown": True},
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
                url=self.url(f"/api/v1/datasets/{mock_dataset_id}/fields"),
                method="POST",
                status_code=200,
            )

        with httpx.Client():
            if expected_exception:
                with pytest.raises(expected_exception=expected_exception) as excinfo:
                    dataset.name = "new_name"
                    dataset.update()
                assert expected_message in str(excinfo.value)
            else:
                dataset.name = "new_name"
                dataset = dataset.update()
                assert dataset.name == "new_name"

    @pytest.mark.parametrize(
        "status_code, expected_exception, expected_message",
        [
            (200, None, None),
            (400, BadRequestError, "BadRequestError"),
            (403, ForbiddenError, "ForbiddenError"),
            (404, NotFoundError, "NotFoundError"),
            (409, ConflictError, "ConflictError"),
            (422, UnprocessableEntityError, "UnprocessableEntityError"),
            (500, InternalServerError, "InternalServerError"),
        ],
    )
    def test_delete_dataset(self, httpx_mock: HTTPXMock, status_code, expected_exception, expected_message, dataset):
        mock_dataset_id = dataset.id
        mock_return_value = dataset.serialize()
        api_url = "http://test_url"
        httpx_mock.add_response(
            json=mock_return_value,
            url=f"{api_url}/api/v1/datasets/{mock_dataset_id}",
            method="DELETE",
            status_code=status_code,
        )
        with httpx.Client():
            if expected_exception:
                with pytest.raises(expected_exception=expected_exception) as excinfo:
                    dataset.delete()
                assert expected_message in str(excinfo.value)
            else:
                dataset.delete()
                assert dataset.name == mock_return_value["name"]

    def _mock_dataset_settings(self, httpx_mock: HTTPXMock, dataset_id: uuid.UUID, dataset_dict: dict):
        mock_field = {
            "id": str(uuid.uuid4()),
            "name": "text",
            "settings": {"type": "text", "use_markdown": True},
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        mock_question = {
            "id": str(uuid.uuid4()),
            "name": "response",
            "settings": {"type": "text", "use_markdown": True},
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        httpx_mock.add_response(
            json=dataset_dict,
            url=self.url(f"/api/v1/datasets/{dataset_id}"),
            method="PATCH",
            status_code=200,
        )
        httpx_mock.add_response(
            json=mock_field, url=self.url(f"/api/v1/datasets/{dataset_id}/fields"), method="POST", status_code=200
        )
        httpx_mock.add_response(
            json=mock_question, url=self.url(f"/api/v1/datasets/{dataset_id}/questions"), method="POST", status_code=200
        )


class TestDatasetsAPI:
    def test_delete_dataset(self, httpx_mock: HTTPXMock):
        # TODO: Add a test for the delete method in client
        mock_dataset_id = uuid.uuid4()
        mock_return_value = {
            "id": str(mock_dataset_id),
            "name": "dataset-01",
            "status": "draft",
            "allow_extra_metadata": False,
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        httpx_mock.add_response(
            json=mock_return_value,
            url=f"http://test_url/api/v1/datasets/{mock_dataset_id}",
            method="DELETE",
            status_code=200,
        )
        with httpx.Client() as client:
            client = rg.Argilla("http://test_url")
            client.api.datasets.delete(mock_dataset_id)
            pytest.raises(httpx.HTTPError, client.api.datasets.get, mock_dataset_id)

    def test_publish_dataset(self, httpx_mock: HTTPXMock):
        # TODO: Add a test for the publish method in client when dataset is finished
        mock_dataset_id = uuid.uuid4()
        mock_return_value = {
            "id": str(mock_dataset_id),
            "name": "dataset-01",
            "status": "ready",
            "allow_extra_metadata": False,
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        httpx_mock.add_response(
            json=mock_return_value,
            url=f"http://test_url/api/v1/datasets/{mock_dataset_id}/publish",
            method="PUT",
            status_code=200,
        )
        httpx_mock.add_response(
            json=mock_return_value,
            url=f"http://test_url/api/v1/datasets/{mock_dataset_id}",
            method="GET",
            status_code=200,
        )
        with httpx.Client() as client:
            client = rg.Argilla("http://test_url")
            client.api.datasets.publish(mock_dataset_id)
            dataset = client.api.datasets.get(mock_dataset_id)
            assert dataset.status == "ready"
            assert dataset.id == mock_dataset_id
            assert dataset.name == "dataset-01"

    def test_get_by_name_and_workspace_id(self, httpx_mock: HTTPXMock):
        mock_workspace_id = uuid.uuid4()
        mock_dataset_id = uuid.uuid4()
        mock_return_value = {
            "items": [
                {
                    "id": mock_dataset_id.hex,
                    "name": "dataset-01",
                    "status": "ready",
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "workspace_id": mock_workspace_id.hex,
                }
            ]
        }
        api_url = "http://test_url"
        httpx_mock.add_response(
            json=mock_return_value, url=f"{api_url}/api/v1/me/datasets", method="GET", status_code=200
        )
        with httpx.Client():
            client = rg.Argilla(api_url)
            dataset = client.api.datasets.get_by_name_and_workspace_id("dataset-01", mock_workspace_id)
            assert mock_dataset_id.hex == mock_return_value["items"][0]["id"]
            assert dataset.name == mock_return_value["items"][0]["name"]
            assert dataset.status == mock_return_value["items"][0]["status"]
            assert dataset.workspace_id.hex == mock_return_value["items"][0]["workspace_id"]
            assert dataset.inserted_at.isoformat() == mock_return_value["items"][0]["inserted_at"]
            assert dataset.updated_at.isoformat() == mock_return_value["items"][0]["updated_at"]
