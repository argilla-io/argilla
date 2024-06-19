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
from argilla_server.commons.models import TaskType
from argilla_v1.client.sdk.commons.api import bulk
from argilla_v1.client.sdk.commons.models import (
    BulkResponse,
)


def test_text2text_bulk(sdk_client, mocked_client, bulk_text2text_data, monkeypatch):
    monkeypatch.setattr(httpx, "post", mocked_client.post)

    dataset_name = "test_dataset"

    mocked_client.delete(f"/api/datasets/{dataset_name}")
    mocked_client.post("/api/datasets", json={"name": dataset_name, "task": TaskType.text2text})

    response = bulk(sdk_client, name=dataset_name, json_body=bulk_text2text_data)
    assert isinstance(response, BulkResponse)


def test_textclass_bulk(sdk_client, mocked_client, bulk_textclass_data, monkeypatch):
    monkeypatch.setattr(httpx, "post", mocked_client.post)

    dataset_name = "test_dataset"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    mocked_client.post("/api/datasets", json={"name": dataset_name, "task": TaskType.text_classification})

    response = bulk(sdk_client, name=dataset_name, json_body=bulk_textclass_data)
    assert isinstance(response, BulkResponse)


def test_tokenclass_bulk(sdk_client, mocked_client, bulk_tokenclass_data, monkeypatch):
    monkeypatch.setattr(httpx, "post", mocked_client.post)

    dataset_name = "test_dataset"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    mocked_client.post("/api/datasets", json={"name": dataset_name, "task": TaskType.token_classification})

    response = bulk(sdk_client, name=dataset_name, json_body=bulk_tokenclass_data)
    assert isinstance(response, BulkResponse)
