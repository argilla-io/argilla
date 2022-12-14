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

from argilla.server.apis.v0.models.text_classification import (
    TextClassificationBulkRequest,
    TextClassificationRecord,
)


def create_dataset(mocked_client):
    dataset = "test-dataset"
    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
    tags = {"env": "test", "class": "text classification"}
    metadata = {"config": {"the": "config"}}

    classification_bulk = TextClassificationBulkRequest(
        tags=tags,
        metadata=metadata,
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
    response = mocked_client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=classification_bulk.dict(by_alias=True),
    )

    assert response.status_code == 200
    return dataset


def test_get_record_by_id(mocked_client):
    dataset = create_dataset(mocked_client)

    record_id = 0
    response = mocked_client.get(f"/api/datasets/{dataset}/records/{record_id}")

    assert response.status_code == 200
    record = TextClassificationRecord.parse_obj(response.json())
    assert record.id == record_id


def test_get_record_by_id_not_found(mocked_client):
    dataset = create_dataset(mocked_client)

    record_id = "not-found"
    response = mocked_client.get(f"/api/datasets/{dataset}/records/{record_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::RecordNotFound",
            "params": {
                "dataset": "argilla.test-dataset",
                "id": record_id,
                "name": "argilla.test-dataset.not-found",
                "type": "Record",
            },
        }
    }
