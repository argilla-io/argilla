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
import argilla as rg
import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.commons.models import TaskType
from argilla.server.models import User
from starlette.testclient import TestClient

from tests.factories import AnnotatorFactory, WorkspaceFactory


def create_dataset(client, name: str):
    response = client.post("/api/datasets", json={"name": name, "task": TaskType.text_classification})
    assert response.status_code == 200


def test_create_dataset_settings(mocked_client):
    name = "test_create_dataset_settings"
    rg.delete(name)
    create_dataset(mocked_client, name)

    response = create_settings(mocked_client, name)
    assert response.status_code == 200

    created = response.json()
    response = fetch_settings(mocked_client, name)
    assert response.json() == created


def create_settings(mocked_client, name):
    response = mocked_client.put(
        f"/api/datasets/{TaskType.text_classification}/{name}/settings",
        json={"label_schema": {"labels": ["Label1", "Label2"]}},
    )
    return response


def test_get_dataset_settings_not_found(mocked_client):
    name = "test_get_dataset_settings"
    rg.delete(name)
    create_dataset(mocked_client, name)

    response = fetch_settings(mocked_client, name)
    assert response.status_code == 404


def test_delete_settings(mocked_client):
    name = "test_delete_settings"
    rg.delete(name)

    create_dataset(mocked_client, name)
    assert create_settings(mocked_client, name).status_code == 200

    response = mocked_client.delete(f"/api/datasets/{TaskType.text_classification}/{name}/settings")
    assert response.status_code == 200
    assert fetch_settings(mocked_client, name).status_code == 404


def test_validate_settings_when_logging_data(mocked_client):
    name = "test_validate_settings_when_logging_data"
    rg.delete(name)

    create_dataset(mocked_client, name)
    assert create_settings(mocked_client, name).status_code == 200

    response = log_some_data(mocked_client, name)
    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::BadRequestError",
            "params": {
                "message": "Provided records contain the Mocking label, "
                "that is not included in the labels schema.\n"
                "Please, annotate your records using labels "
                "defined in the labels schema."
            },
        }
    }


def test_validate_settings_after_logging(mocked_client):
    name = "test_validate_settings_after_logging"

    rg.delete(name)
    response = log_some_data(mocked_client, name)
    assert response.status_code == 200

    response = create_settings(mocked_client, name)
    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::BadRequestError",
            "params": {
                "message": "The label Mocking was found in the dataset but "
                "not in provided labels schema. \n"
                "Please, provide a valid labels schema "
                "according to stored records in the dataset"
            },
        }
    }


def log_some_data(mocked_client, name):
    return mocked_client.post(
        f"/api/datasets/{name}/TextClassification:bulk",
        json={
            "records": [
                {
                    "inputs": {"data": "my data"},
                    "prediction": {
                        "agent": "test",
                        "labels": [
                            {"class": "Mocking", "score": 0.2},
                        ],
                    },
                }
            ]
        },
    )


# TODO: These tests are the same for token an text classification. We will move them to a common test_dataset_settings
#  module where settings will be tested in a per-task fashion.
@pytest.mark.parametrize("task", [TaskType.text_classification, TaskType.token_classification])
def test_save_settings_as_annotator(test_client: TestClient, argilla_auth_header: dict, task: TaskType):
    dataset_name = "test_save_settings_as_annotator"
    workspace_name = "workspace-a"
    annotator = AnnotatorFactory.create(workspaces=[WorkspaceFactory.build(name=workspace_name)])

    test_client.delete(f"/api/datasets/{dataset_name}?workspace={workspace_name}", headers=argilla_auth_header)

    response = test_client.post(
        "/api/datasets",
        json={"name": dataset_name, "task": task, "workspace": workspace_name},
        headers=argilla_auth_header,
    )
    assert response.status_code == 200

    response = test_client.put(
        f"/api/datasets/{dataset_name}/{task}/settings?workspace={workspace_name}",
        json={"label_schema": {"labels": ["Label1", "Label2"]}},
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::ForbiddenOperationError",
            "params": {"detail": "You don't have the necessary permissions to " "save settings for this dataset."},
        }
    }


@pytest.mark.parametrize("task", [TaskType.text_classification, TaskType.token_classification])
def test_delete_settings_as_annotator(test_client: TestClient, argilla_auth_header: dict, task: TaskType):
    dataset_name = "test_delete_settings_as_annotator"
    workspace_name = "workspace-a"
    annotator = AnnotatorFactory.create(workspaces=[WorkspaceFactory.build(name=workspace_name)])

    test_client.delete(f"/api/datasets/{dataset_name}?workspace={workspace_name}", headers=argilla_auth_header)

    response = test_client.post(
        "/api/datasets",
        json={"name": dataset_name, "task": task, "workspace": workspace_name},
        headers=argilla_auth_header,
    )
    assert response.status_code == 200

    response = test_client.delete(
        f"/api/datasets/{dataset_name}/{task}/settings?workspace={workspace_name}",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::ForbiddenOperationError",
            "params": {"detail": "You don't have the necessary permissions to " "delete settings for this dataset."},
        }
    }


@pytest.mark.parametrize("task", [TaskType.text_classification, TaskType.token_classification])
def test_get_settings_as_annotator(test_client: TestClient, argilla_auth_header: dict, task: TaskType):
    dataset_name = "test_get_settings_as_annotator"
    workspace_name = "workspace-a"
    annotator = AnnotatorFactory.create(workspaces=[WorkspaceFactory.build(name=workspace_name)])

    test_client.delete(f"/api/datasets/{dataset_name}?workspace={workspace_name}", headers=argilla_auth_header)

    response = test_client.post(
        "/api/datasets",
        json={"name": dataset_name, "task": task, "workspace": workspace_name},
        headers=argilla_auth_header,
    )
    assert response.status_code == 200

    response = test_client.put(
        f"/api/datasets/{dataset_name}/{task}/settings?workspace={workspace_name}",
        json={"label_schema": {"labels": ["Label1", "Label2"]}},
        headers=argilla_auth_header,
    )

    stored_settings = response.json()
    response = test_client.get(
        f"/api/datasets/{dataset_name}/{task}/settings?workspace={workspace_name}",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 200
    assert response.json() == stored_settings


def fetch_settings(mocked_client, name):
    return mocked_client.get(f"/api/datasets/{TaskType.text_classification}/{name}/settings")
