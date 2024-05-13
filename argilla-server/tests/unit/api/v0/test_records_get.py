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
from typing import Type

import pytest
from argilla_server.apis.v0.models.commons.model import BaseRecord
from argilla_server.apis.v0.models.text2text import (
    Text2TextBulkRequest,
    Text2TextRecord,
)
from argilla_server.apis.v0.models.text_classification import (
    TextClassificationBulkRequest,
    TextClassificationRecord,
)
from argilla_server.apis.v0.models.token_classification import (
    TokenClassificationBulkRequest,
    TokenClassificationRecord,
)
from argilla_server.commons.models import TaskType
from argilla_server.models import User
from httpx import AsyncClient

from tests.factories import WorkspaceFactory


async def create_dataset(async_client: "AsyncClient", task: TaskType, workspace_name: str):
    dataset = "test-dataset"
    record_text = "This is my text"
    response = await async_client.delete(f"/api/datasets/{dataset}", params={"workspace": workspace_name})
    assert response.status_code in [200, 404]

    response = await async_client.post(
        "/api/datasets", json={"name": dataset, "workspace": workspace_name, "task": task.value}
    )
    assert response.status_code == 200
    tags = {"env": "test", "type": task}

    if task == TaskType.text_classification:
        bulk_data = TextClassificationBulkRequest(
            tags=tags,
            records=[
                TextClassificationRecord(
                    **{
                        "id": 0,
                        "inputs": {"data": "my data"},
                        "prediction": {
                            "agent": "test",
                            "labels": [
                                {"class": "Test", "score": 0.3},
                                {"class": "Mocking", "score": 0.7},
                            ],
                        },
                    }
                )
            ],
        )
    elif task == TaskType.token_classification:
        bulk_data = TokenClassificationBulkRequest(
            tags=tags,
            records=[
                TokenClassificationRecord.parse_obj(
                    {
                        "id": 0,
                        "text": record_text,
                        "tokens": record_text.split(),
                    }
                )
            ],
        )
    else:
        bulk_data = Text2TextBulkRequest(
            tags=tags,
            records=[
                Text2TextRecord.parse_obj(
                    {
                        "id": 0,
                        "text": record_text,
                    }
                )
            ],
        )

    response = await async_client.post(
        f"/api/datasets/{dataset}/{task}:bulk", json=bulk_data.dict(by_alias=True), params={"workspace": workspace_name}
    )

    assert response.status_code == 200
    return dataset


@pytest.mark.parametrize(
    ("task", "expected_record_class"),
    [
        (TaskType.token_classification, TokenClassificationRecord),
        (TaskType.text_classification, TextClassificationRecord),
        (TaskType.text2text, Text2TextRecord),
    ],
)
@pytest.mark.asyncio
async def test_get_record_by_id(
    async_client: "AsyncClient",
    owner_auth_header: dict,
    task: TaskType,
    expected_record_class: Type[BaseRecord],
):
    workspace = await WorkspaceFactory.create()
    async_client.headers.update(owner_auth_header)
    dataset = await create_dataset(async_client, task=task, workspace_name=workspace.name)

    record_id = 0
    response = await async_client.get(
        f"/api/datasets/{dataset}/records/{record_id}", params={"workspace": workspace.name}
    )

    assert response.status_code == 200
    record = expected_record_class.parse_obj(response.json())
    assert record.id == record_id


@pytest.mark.parametrize(
    "task",
    [TaskType.token_classification, TaskType.text_classification, TaskType.text2text],
)
@pytest.mark.asyncio
async def test_get_record_by_id_not_found(async_client: "AsyncClient", owner_auth_header: dict, task: TaskType):
    async_client.headers.update(owner_auth_header)
    workspace = await WorkspaceFactory.create()
    dataset = await create_dataset(async_client, task=task, workspace_name=workspace.name)

    record_id = "not-found"
    response = await async_client.get(
        f"/api/datasets/{dataset}/records/{record_id}", params={"workspace": workspace.name}
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::RecordNotFound",
            "params": {
                "dataset": f"{workspace.name}.test-dataset",
                "id": record_id,
                "name": f"{workspace.name}.test-dataset.not-found",
                "type": "Record",
            },
        }
    }
