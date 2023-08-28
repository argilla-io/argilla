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

import httpx
import pytest
from argilla.client.client import Argilla
from argilla.client.sdk.commons.errors import (
    GenericApiError,
    NotFoundApiError,
    ValidationApiError,
)
from argilla.client.sdk.datasets.api import _build_response, get_dataset, list_datasets
from argilla.client.sdk.datasets.models import Dataset, TaskType
from argilla.client.sdk.text_classification.models import TextClassificationBulkData
from argilla.server.models import UserRole

from tests.factories import DatasetFactory, UserFactory, WorkspaceFactory


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_get_dataset(role: UserRole):
    # create test dataset
    bulk_data = TextClassificationBulkData(records=[])
    dataset_name = "test_dataset"

    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create(role=role, workspaces=[workspace])
    api = Argilla(api_key=user.api_key, workspace=workspace.name)

    api.delete(dataset_name)
    assert (
        api.http_client.httpx.post(
            "/api/datasets",
            json={"name": dataset_name, "workspace": workspace.name, "task": TaskType.text_classification.value},
        ).status_code
        == 200
    )
    api.http_client.httpx.post(
        f"/api/datasets/{dataset_name}/TextClassification:bulk", json=bulk_data.dict(by_alias=True)
    )

    response = get_dataset(client=api.http_client, name="test_dataset")

    assert response.status_code == 200
    assert isinstance(response.parsed, Dataset)


@pytest.mark.parametrize(
    "status_code, expected",
    [
        (404, NotFoundApiError),
        (500, GenericApiError),
        (422, ValidationApiError),
    ],
)
def test_build_response(status_code, expected):
    httpx_response = httpx.Response(
        status_code=status_code,
        json={"detail": {"code": "error.code", "params": {"foo": "bar"}}},
    )
    with pytest.raises(expected):
        _build_response(httpx_response, name="mock-ds")


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_list_datasets(role: UserRole) -> None:
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create(role=role, workspaces=[workspace])

    api = Argilla(api_key=user.api_key, workspace=workspace.name)
    assert (
        api.http_client.httpx.post(
            "/api/datasets",
            json={"name": "test_dataset", "workspace": workspace.name, "task": TaskType.text_classification.value},
        ).status_code
        == 200
    )

    response = list_datasets(api.client, workspace=workspace.name)
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) == 1
    assert isinstance(response.parsed[0], Dataset)
