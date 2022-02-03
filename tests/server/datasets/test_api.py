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

from rubrix.server.datasets.model import Dataset
from rubrix.server.tasks.text_classification import TextClassificationBulkData
from tests.server.test_helpers import client


def test_delete_dataset():
    dataset = "test_delete_dataset"
    create_mock_dataset(dataset)

    delete_dataset(dataset)

    response = client.get(f"/api/datasets/{dataset}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "rubrix.api.errors::EntityNotFoundError",
            "params": {"name": "test_delete_dataset", "type": "Dataset"},
        }
    }


def test_dataset_naming_validation():
    request = TextClassificationBulkData(records=[])
    dataset = "Wrong dataset name"

    response = client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=request.dict(by_alias=True),
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "rubrix.api.errors::ValidationError",
            "params": {
                "errors": [
                    {
                        "ctx": {"pattern": "^(?!-|_)[a-z0-9-_]+$"},
                        "loc": ["name"],
                        "msg": "string does not match regex " '"^(?!-|_)[a-z0-9-_]+$"',
                        "type": "value_error.str.regex",
                    }
                ],
                "model": "CreationDatasetRequest",
            },
        }
    }

    response = client.post(
        f"/api/datasets/{dataset}/TokenClassification:bulk",
        json=request.dict(by_alias=True),
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "rubrix.api.errors::ValidationError",
            "params": {
                "errors": [
                    {
                        "ctx": {"pattern": "^(?!-|_)[a-z0-9-_]+$"},
                        "loc": ["name"],
                        "msg": "string does not match regex " '"^(?!-|_)[a-z0-9-_]+$"',
                        "type": "value_error.str.regex",
                    }
                ],
                "model": "CreationDatasetRequest",
            },
        }
    }


def test_list_datasets():
    dataset = "test_list_datasets"
    delete_dataset(dataset)

    create_mock_dataset(dataset)

    response = client.get("/api/datasets/")
    assert response.status_code == 200

    datasets = [Dataset.parse_obj(item) for item in response.json()]
    assert len(datasets) > 0
    assert dataset in [ds.id for ds in datasets]


def test_update_dataset():
    dataset = "test_update_dataset"
    delete_dataset(dataset)
    create_mock_dataset(dataset)

    response = client.patch(
        f"/api/datasets/{dataset}", json={"metadata": {"new": "value"}}
    )
    assert response.status_code == 200

    response = client.get(f"/api/datasets/{dataset}")
    assert response.status_code == 200
    ds = Dataset.parse_obj(response.json())
    assert ds.metadata["new"] == "value"


def test_open_and_close_dataset():
    dataset = "test_open_and_close_dataset"
    delete_dataset(dataset)
    create_mock_dataset(dataset)

    assert client.put(f"/api/datasets/{dataset}:close").status_code == 200

    response = client.post(f"/api/datasets/{dataset}/TextClassification:search")
    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": "rubrix.api.errors::ClosedDatasetError",
            "params": {"name": dataset},
        }
    }

    assert client.put(f"/api/datasets/{dataset}:open").status_code == 200
    assert (
        client.post(f"/api/datasets/{dataset}/TextClassification:search").status_code
        == 200
    )


def delete_dataset(dataset):
    assert client.delete(f"/api/datasets/{dataset}").status_code == 200


def create_mock_dataset(dataset):
    client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkData(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=[],
        ).dict(by_alias=True),
    )
