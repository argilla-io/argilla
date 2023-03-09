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
from argilla.server.commons.models import TaskType


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


def fetch_settings(mocked_client, name):
    return mocked_client.get(f"/api/datasets/{TaskType.text_classification}/{name}/settings")
