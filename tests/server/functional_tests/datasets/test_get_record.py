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
import pytest
from argilla.server.apis.v0.models.text2text import (
    Text2TextBulkRequest,
    Text2TextRecord,
)
from argilla.server.apis.v0.models.text_classification import (
    TextClassificationBulkRequest,
    TextClassificationRecord,
)
from argilla.server.apis.v0.models.token_classification import (
    TokenClassificationBulkRequest,
    TokenClassificationRecord,
)
from argilla.server.commons.models import TaskType


def create_dataset(
    mocked_client,
    task: TaskType,
):
    dataset = "test-dataset"
    record_text = "This is my text"
    assert mocked_client.delete(f"/api/datasets/{dataset}").status_code == 200
    tags = {
        "env": "test",
        "type": task,
    }

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

    response = mocked_client.post(
        f"/api/datasets/{dataset}/{task}:bulk",
        json=bulk_data.dict(by_alias=True),
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
def test_get_record_by_id(mocked_client, task, expected_record_class):
    dataset = create_dataset(
        mocked_client,
        task=task,
    )

    record_id = 0
    response = mocked_client.get(f"/api/datasets/{dataset}/records/{record_id}")

    assert response.status_code == 200
    record = expected_record_class.parse_obj(response.json())
    assert record.id == record_id


@pytest.mark.parametrize(
    "task",
    [
        TaskType.token_classification,
        TaskType.text_classification,
        TaskType.text2text,
    ],
)
def test_get_record_by_id_not_found(mocked_client, task):
    dataset = create_dataset(
        mocked_client,
        task=task,
    )

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
