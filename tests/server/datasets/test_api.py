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
from rubrix.server.tasks.text_classification import TextClassificationBulkData

from tests.server.test_helpers import client


def test_delete_dataset():
    dataset = "test_delete_dataset"

    client.post(
        f"/api/datasets/{dataset}/TextClassification:bulk",
        json=TextClassificationBulkData(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=[],
        ).dict(by_alias=True),
    )

    assert client.delete(f"/api/datasets/{dataset}").status_code == 200
    assert client.get(f"/api/datasets/{dataset}").status_code == 404


def test_dataset_naming_validation():
    request = TextClassificationBulkData(records=[])
    dataset = "Wrong dataset name"

    assert (
        client.post(
            f"/api/datasets/{dataset}/TextClassification:bulk",
            json=request.dict(by_alias=True),
        ).status_code
        == 422
    )

    assert (
        client.post(
            f"/api/datasets/{dataset}/TokenClassification:bulk",
            json=request.dict(by_alias=True),
        ).status_code
        == 422
    )
