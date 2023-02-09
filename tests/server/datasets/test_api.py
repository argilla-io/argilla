#  coding=utf-8
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
from typing import Optional

from argilla.server.apis.v0.models.datasets import Dataset
from argilla.server.apis.v0.models.text_classification import (
    TextClassificationBulkRequest,
)
from argilla.server.commons.models import TaskType
from tests.helpers import SecuredClient


def test_delete_dataset(mocked_client):
    dataset = "test_delete_dataset"
    create_mock_dataset(mocked_client, dataset)

    delete_dataset(mocked_client, dataset)

    response = mocked_client.get(f"/api/datasets/{dataset}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::EntityNotFoundError",
            "params": {"name": "test_delete_dataset", "type": "ServiceDataset"},
        }
    }


def test_create_dataset(mocked_client):
    dataset_name = "test_create_dataset"
    delete_dataset(mocked_client, dataset_name)
    request = dict(
        name=dataset_name,
        task=TaskType.text_classification,
        tags={"env": "test", "class": "text classification"},
        metadata={"config": {"the": "config"}},
    )
    response = mocked_client.post(
        "/api/datasets",
        json=request,
    )
    assert response.status_code == 200
    dataset = Dataset.parse_obj(response.json())
    assert dataset.created_by == "argilla"
    assert dataset.metadata == request["metadata"]
    assert dataset.tags == request["tags"]
    assert dataset.name == dataset_name
    assert dataset.owner == "argilla"
    assert dataset.task == TaskType.text_classification

    response = mocked_client.post(
        "/api/datasets",
        json=request,
    )
    assert response.status_code == 409


def test_fetch_dataset_using_workspaces(mocked_client: SecuredClient):
    ws = "mock-ws"
    dataset_name = "test_fetch_dataset_using_workspaces"
    mocked_client.add_workspaces_to_argilla_user([ws])

    delete_dataset(mocked_client, dataset_name, workspace=ws)
    delete_dataset(mocked_client, dataset_name)
    request = dict(
        name=dataset_name,
        task=TaskType.text_classification,
    )
    response = mocked_client.post(
        f"/api/datasets?workspace={ws}",
        json=request,
    )

    assert response.status_code == 200, response.json()
    dataset = Dataset.parse_obj(response.json())
    assert dataset.created_by == "argilla"
    assert dataset.name == dataset_name
    assert dataset.owner == ws
    assert dataset.task == TaskType.text_classification

    response = mocked_client.post(
        f"/api/datasets?workspace={ws}",
        json=request,
    )
    assert response.status_code == 409, response.json()

    response = mocked_client.post(
        "/api/datasets",
        json=request,
    )

    assert response.status_code == 200, response.json()
    dataset = Dataset.parse_obj(response.json())
    assert dataset.created_by == "argilla"
    assert dataset.name == dataset_name
    assert dataset.owner == "argilla"
    assert dataset.task == TaskType.text_classification


def test_dataset_naming_validation(mocked_client):
    request = TextClassificationBulkRequest(records=[])
    dataset = "Wrong dataset name"

    response = mocked_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=request.dict(by_alias=True),
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::ValidationError",
            "params": {
                "errors": [
                    {
                        "ctx": {"pattern": "^(?!-|_)[a-z0-9-_]+$"},
                        "loc": ["name"],
                        "msg": "string does not match regex " '"^(?!-|_)[a-z0-9-_]+$"',
                        "type": "value_error.str.regex",
                    }
                ],
                "model": "TextClassificationDataset",
            },
        }
    }

    response = mocked_client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=request.dict(by_alias=True),
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::ValidationError",
            "params": {
                "errors": [
                    {
                        "ctx": {"pattern": "^(?!-|_)[a-z0-9-_]+$"},
                        "loc": ["name"],
                        "msg": "string does not match regex " '"^(?!-|_)[a-z0-9-_]+$"',
                        "type": "value_error.str.regex",
                    }
                ],
                "model": "TokenClassificationDataset",
            },
        }
    }


def test_list_datasets(mocked_client):
    dataset = "test_list_datasets"
    delete_dataset(mocked_client, dataset)

    create_mock_dataset(mocked_client, dataset)

    response = mocked_client.get("/api/datasets/")
    assert response.status_code == 200

    datasets = [Dataset.parse_obj(item) for item in response.json()]
    assert len(datasets) > 0
    assert dataset in [ds.name for ds in datasets]


def test_update_dataset(mocked_client):
    dataset = "test_update_dataset"
    delete_dataset(mocked_client, dataset)
    create_mock_dataset(mocked_client, dataset)

    response = mocked_client.patch(
        f"/api/datasets/{dataset}", json={"metadata": {"new": "value"}}
    )
    assert response.status_code == 200

    response = mocked_client.get(f"/api/datasets/{dataset}")
    assert response.status_code == 200
    ds = Dataset.parse_obj(response.json())
    assert ds.metadata["new"] == "value"


def test_open_and_close_dataset(mocked_client):
    dataset = "test_open_and_close_dataset"
    delete_dataset(mocked_client, dataset)
    create_mock_dataset(mocked_client, dataset)

    assert mocked_client.put(f"/api/datasets/{dataset}:close").status_code == 200

    response = mocked_client.post(f"/api/datasets/{dataset}/TextClassification:search")
    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::ClosedDatasetError",
            "params": {"name": dataset},
        }
    }

    assert mocked_client.put(f"/api/datasets/{dataset}:open").status_code == 200
    assert (
        mocked_client.post(
            f"/api/datasets/{dataset}/TextClassification:search"
        ).status_code
        == 200
    )


def delete_dataset(client, dataset, workspace: Optional[str] = None):
    url = f"/api/datasets/{dataset}"
    if workspace:
        url += f"?workspace={workspace}"
    assert client.delete(url).status_code == 200


def create_mock_dataset(client, dataset, records=[]):
    client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )


def test_delete_records(mocked_client):
    dataset_name = "test_delete_records"
    delete_dataset(mocked_client, dataset_name)

    create_mock_dataset(
        mocked_client,
        dataset=dataset_name,
        records=[
            {
                "id": i,
                "inputs": {"text": f"This is a text for id {i}"},
            }
            for i in range(1, 100)
        ],
    )
    response = mocked_client.delete(
        f"/api/datasets/{dataset_name}/data",
        json={"ids": [1]},
    )
    assert response.status_code == 200
    assert response.json() == {"matched": 1, "processed": 1}

    try:
        mocked_client.change_current_user("mock-user")
        response = mocked_client.delete(f"/api/datasets/{dataset_name}/data")
        assert response.status_code == 403
        assert response.json() == {
            "detail": {
                "code": "argilla.api.errors::ForbiddenOperationError",
                "params": {
                    "detail": "You don't have the necessary permissions to delete records on this dataset."
                    " Only dataset creators or administrators can delete datasets"
                },
            }
        }

        response = mocked_client.delete(
            f"/api/datasets/{dataset_name}/data?mark_as_discarded=true"
        )
        assert response.status_code == 200
        assert response.json() == {
            "matched": 99,
            "processed": 98,
        }  # different values are caused by conflicts found
    finally:
        mocked_client.reset_default_user()
