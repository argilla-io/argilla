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
from typing import TYPE_CHECKING

import pytest
from argilla_server.apis.v0.models.text2text import Text2TextBulkRequest, Text2TextRecord, Text2TextRecordInputs
from argilla_server.apis.v0.models.text_classification import TextClassificationBulkRequest, TextClassificationRecord
from argilla_server.apis.v0.models.token_classification import TokenClassificationBulkRequest, TokenClassificationRecord
from argilla_server.commons.models import TaskType
from argilla_server.constants import API_KEY_HEADER_NAME
from argilla_server.models import User, UserRole

from tests.factories import UserFactory, WorkspaceFactory

if TYPE_CHECKING:
    from httpx import AsyncClient


async def create_dataset(async_client: "AsyncClient", workspace_name: str, task: TaskType) -> str:
    dataset_name = "test_dataset"
    params = {"workspace": workspace_name}

    response = await async_client.delete(f"/api/datasets/{dataset_name}", params=params)
    assert response.status_code == 200

    response = await async_client.post(
        f"/api/datasets",
        json={"name": dataset_name, "task": task, "workspace": workspace_name},
    )
    assert response.status_code == 200

    def text_classification_request():
        return TextClassificationBulkRequest(
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

    def token_classification_request():
        return TokenClassificationBulkRequest(
            records=[
                TokenClassificationRecord.parse_obj(data)
                for data in [
                    {
                        "id": 0,
                        "tokens": "This is a text".split(" "),
                        "raw_text": "This is a text",
                        "metadata": {"field_one": "value one", "field_two": "value 2"},
                        "prediction": {
                            "agent": "test",
                            "entities": [
                                {"start": 0, "end": 4, "label": "PERSON"},
                                {"start": 5, "end": 7, "label": "ORG"},
                            ],
                        },
                    },
                    {
                        "id": 1,
                        "tokens": "This is a text".split(" "),
                        "raw_text": "This is a text",
                        "metadata": {"field_one": "value one", "field_two": "value 2"},
                        "prediction": {"agent": "test", "entities": [{"start": 0, "end": 4, "label": "PERSON"}]},
                    },
                    {
                        "id": 2,
                        "tokens": "This is a text".split(" "),
                        "raw_text": "This is a text",
                        "metadata": {"field_one": "value one", "field_two": "value 2"},
                        "annotation": {"agent": "test", "entities": [{"start": 0, "end": 4, "label": "ORG"}]},
                    },
                ]
            ],
        )

    def text2text_request():
        return Text2TextBulkRequest(
            records=[
                Text2TextRecordInputs.parse_obj(
                    {
                        "id": 0,
                        "text": "This is a text data",
                        "predictions": {"test": {"sentences": [{"text": "This is a test data", "score": 0.6}]}},
                    }
                ),
                Text2TextRecordInputs.parse_obj(
                    {
                        "id": 1,
                        "text": "Another data",
                        "annotations": {
                            "annotator-1": {"sentences": [{"text": "THis is a test data"}]},
                            "annotator-2": {"sentences": [{"text": "This IS the test datay"}]},
                        },
                    }
                ),
            ]
        )

    request_builder = {
        TaskType.text2text: text2text_request,
        TaskType.token_classification: token_classification_request,
        TaskType.text_classification: text_classification_request,
    }[task]

    response = await async_client.post(
        f"/api/datasets/{dataset_name}/{task}:bulk",
        json=request_builder().dict(by_alias=True, exclude_none=True),
        params=params,
    )
    assert response.status_code == 200

    return dataset_name


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.parametrize(
    ("task", "expected_record_class"),
    [
        (TaskType.token_classification, TokenClassificationRecord),
        (TaskType.text_classification, TextClassificationRecord),
        (TaskType.text2text, Text2TextRecord),
    ],
)
@pytest.mark.asyncio
async def test_update_record_ok(async_client: "AsyncClient", owner: User, task, expected_record_class, role: UserRole):
    async_client.headers.update({API_KEY_HEADER_NAME: owner.api_key})

    expected_id = 0
    workspace = await WorkspaceFactory.create()
    dataset = await create_dataset(async_client, workspace_name=workspace.name, task=task)
    user = await UserFactory.create(role=role, workspaces=[workspace])

    text = "A new value for record 0"
    response = await async_client.patch(
        f"/api/datasets/{dataset}/records/{expected_id}",
        json={"metadata": {"new_value": text}},
        headers={API_KEY_HEADER_NAME: user.api_key},
        params={"workspace": workspace.name},
    )
    assert response.status_code == 200, response.json()
    updated_record = expected_record_class.parse_obj(response.json())
    assert updated_record.metadata["new_value"] == text

    response = await async_client.post(
        f"/api/datasets/{dataset}/{task}:search",
        json={"query": {"ids": [expected_id]}},
        headers={API_KEY_HEADER_NAME: user.api_key},
        params={"workspace": workspace.name},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    record = data["records"][0]

    updated_record.metrics = {}
    assert updated_record == expected_record_class.parse_obj(record)


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.parametrize(
    "task",
    [
        (TaskType.token_classification),
        (TaskType.text_classification),
        (TaskType.text2text),
    ],
)
@pytest.mark.asyncio
async def test_update_with_not_found(async_client: "AsyncClient", task: TaskType, role: UserRole):
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create(role=role, workspaces=[workspace])

    async_client.headers.update({API_KEY_HEADER_NAME: user.api_key})

    dataset = await create_dataset(async_client, workspace_name=workspace.name, task=task)

    response = await async_client.patch(
        f"/api/datasets/{dataset}/records/not-found",
        json={"status": "Validated"},
        headers={API_KEY_HEADER_NAME: user.api_key},
        params={"workspace": workspace.name},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::RecordNotFound",
            "params": {
                "dataset": f"{workspace.name}.test_dataset",
                "id": "not-found",
                "name": f"{workspace.name}.test_dataset.not-found",
                "type": "Record",
            },
        }
    }


@pytest.mark.asyncio
async def test_with_wrong_values(async_client: "AsyncClient", owner: User):
    async_client.headers.update({API_KEY_HEADER_NAME: owner.api_key})
    workspace = await WorkspaceFactory.create()
    dataset = await create_dataset(async_client, workspace_name=workspace.name, task=TaskType.text_classification)

    response = await async_client.patch(
        f"/api/datasets/{dataset}/records/not-found",
        json={"status": "NOStatus"},
        headers={API_KEY_HEADER_NAME: owner.api_key},
        params={"workspace": workspace.name},
    )

    assert response.status_code == 422
