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

import httpx
import pytest

from rubrix.client.sdk.commons.models import BulkResponse
from rubrix.client.sdk.token_classification.api import bulk, data
from rubrix.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    TokenClassificationBulkData,
    TokenClassificationRecord,
)
from tests.server.test_helpers import client


@pytest.fixture
def bulk_data():
    return TokenClassificationBulkData(
        records=[
            CreationTokenClassificationRecord(
                raw_text="a raw text", tokens=["a", "raw", "text"]
            )
        ]
    )


def test_bulk(sdk_client, bulk_data, monkeypatch):
    monkeypatch.setattr(httpx, "post", client.post)

    dataset_name = "test_dataset"
    client.delete(f"/api/datasets/{dataset_name}")
    response = bulk(sdk_client, name=dataset_name, json_body=bulk_data)
    print(response)

    assert response.status_code == 200
    assert isinstance(response.parsed, BulkResponse)


def test_data(sdk_client, monkeypatch):
    # TODO: Not sure how to test the streaming part of the response here
    monkeypatch.setattr(httpx, "stream", client.stream)

    # create test dataset
    records = [
        CreationTokenClassificationRecord(
            raw_text="a raw text", tokens=["a", "raw", "text"]
        )
        for _ in range(3)
    ]
    bulk_data = TokenClassificationBulkData(records=records)
    dataset_name = "test_dataset"
    client.delete(f"/api/datasets/{dataset_name}")
    client.post(
        f"/api/datasets/{dataset_name}/TokenClassification:bulk",
        json=bulk_data.dict(by_alias=True),
    )

    response = data(sdk_client, name=dataset_name, limit=2)
    assert isinstance(response.parsed[0], TokenClassificationRecord)
    assert len(response.parsed) == 2
