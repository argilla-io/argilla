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


class TestWorkspacesSerialization:
    def test_serialize(self):
        ws = rg.Workspace(
            name="test-workspace",
            id=uuid.uuid4(),
        )

        assert ws.name == ws.serialize()["name"]

    def test_json_serialize_raise_typeerror(self):
        with pytest.raises(TypeError):
            rg.Workspace(
                name="test-workspace",
                id=uuid.uuid4(),
                inserted_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )


class TestWorkspaces:
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
    def test_create_workspace(self, httpx_mock: HTTPXMock, status_code, expected_exception, expected_message):
        mock_name = "test-workspace"
        mock_return_value = {
            "id": str(uuid.uuid4()),
            "name": mock_name,
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        api_url = "http://test_url"
        httpx_mock.add_response(json=mock_return_value, url=f"{api_url}/api/v1/workspaces", status_code=status_code)
        with httpx.Client():
            client = rg.Argilla(api_url=api_url, api_key="admin.apikey")
            if expected_exception:
                with pytest.raises(expected_exception, match=expected_message):
                    ws = rg.Workspace(name="test-workspace", id=uuid.uuid4(), client=client)
                    ws.create()
            else:
                ws = rg.Workspace(name="test-workspace", id=uuid.uuid4(), client=client)
                created_workspace = ws.create()
                assert created_workspace.name == mock_name
                assert created_workspace.id == uuid.UUID(mock_return_value["id"])

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
    def test_get_workspace(self, httpx_mock: HTTPXMock, status_code, expected_exception, expected_message):
        workspace_id = uuid.uuid4()
        mock_return_value = {
            "id": workspace_id.hex,
            "name": "test-workspace",
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        api_url = "http://test_url"
        httpx_mock.add_response(
            json=mock_return_value, url=f"{api_url}/api/v1/workspaces/{workspace_id}", status_code=status_code
        )
        with httpx.Client():
            client = rg.Argilla(api_url="http://test_url", api_key="admin.apikey")

            if expected_exception:
                with pytest.raises(expected_exception, match=expected_message):
                    workspace = rg.Workspace(name="test-workspace", id=workspace_id, client=client)
                    workspace = workspace.get()
            else:
                workspace = rg.Workspace(name="test-workspace", id=workspace_id, client=client)
                workspace = workspace.get()
                assert workspace.name == mock_return_value["name"]
                assert workspace.id == workspace_id

    def test_list_workspaces(self, httpx_mock: HTTPXMock):
        mock_return_value = {
            "items": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "test-workspace",
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "another-test-workspace",
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
            ]
        }
        api_url = "http://test_url"
        httpx_mock.add_response(json=mock_return_value, url=f"{api_url}/api/v1/me/workspaces")
        with httpx.Client():
            client = rg.Argilla(api_url="http://test_url", api_key="admin.apikey")
            workspaces = client.workspaces
        assert len(workspaces) == 2
        for i in range(len(workspaces)):
            assert workspaces[i].name == mock_return_value["items"][i]["name"]
            assert workspaces[i].id == uuid.UUID(mock_return_value["items"][i]["id"])


class TestWorkspacesAPI:
    def test_get_workspace_by_name(self, httpx_mock: HTTPXMock):
        mock_return_value = {
            "items": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "test-workspace",
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "other-workspace",
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
            ]
        }
        api_url = "http://test_url"
        httpx_mock.add_response(json=mock_return_value, url=f"{api_url}/api/v1/me/workspaces")
        with httpx.Client():
            client = rg.Argilla(api_url=api_url, api_key="admin.apikey")
            ws = client.api.workspaces.get_by_name("test-workspace")
            assert ws is not None
            assert ws.name == "test-workspace"
            assert ws.id == uuid.UUID(mock_return_value["items"][0]["id"])

    def test_multiple_clients_create_workspace(self, httpx_mock: HTTPXMock):
        mock_uuid = str(uuid.uuid4())
        mock_name = "local-test-workspace"
        mock_return = {
            "id": mock_uuid,
            "name": mock_name,
            "inserted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        httpx_mock.add_response(
            url="http://localhost:6900/api/v1/workspaces",
            json=mock_return,
        )
        httpx_mock.add_response(
            url="http://argilla.production.net/api/v1/workspaces",
            json=mock_return,
        )
        with httpx.Client():
            local_client = rg.Argilla(api_url="http://localhost:6900", api_key="admin.apikey")
            remote_client = rg.Argilla(api_url="http://argilla.production.net", api_key="admin.apikey")
            assert local_client.api_url == "http://localhost:6900"
            assert remote_client.api_url == "http://argilla.production.net"
            local_workspace = rg.Workspace(name="local-test-workspace", client=local_client)
            local_workspace = local_workspace.create()
            remote_workspace = rg.Workspace(name="remote-test-workspace", client=remote_client)
            remote_workspace = remote_workspace.create()

    def test_delete_workspace(self, httpx_mock: HTTPXMock):
        workspace_id = uuid.uuid4()
        api_url = "http://test_url"
        httpx_mock.add_response(url=f"{api_url}/api/v1/workspaces/{workspace_id}", status_code=204)
        with httpx.Client():
            client = rg.Argilla(api_url=api_url, api_key="admin.apikey")
            client.api.workspaces.delete(workspace_id)

    def test_list_workspace_datasets(self, httpx_mock: HTTPXMock):
        workspace_id = uuid.uuid4()
        mock_return_value = {
            "items": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "test-dataset",
                    "status": "ready",
                    "guidelines": "test-guidelines",
                    "allow_extra_metadata": True,
                    "workspace_id": str(workspace_id),
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "another-test-dataset",
                    "status": "ready",
                    "guidelines": "test-guidelines",
                    "allow_extra_metadata": True,
                    "workspace_id": str(workspace_id),
                    "inserted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
            ]
        }
        api_url = "http://test_url"
        httpx_mock.add_response(json=mock_return_value, url=f"{api_url}/api/v1/me/datasets")
        with httpx.Client():
            client = rg.Argilla(api_url=api_url, api_key="admin.apikey")
            datasets = client.api.datasets.list(workspace_id)
            assert len(datasets) == 2
            for i in range(len(datasets)):
                assert datasets[i].name == mock_return_value["items"][i]["name"]
                assert datasets[i].id == uuid.UUID(mock_return_value["items"][i]["id"])
