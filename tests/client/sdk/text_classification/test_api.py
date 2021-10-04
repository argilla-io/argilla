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
from rubrix._constants import DEFAULT_API_KEY
from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.text_classification.api import bulk
from rubrix.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
)
from rubrix.client.sdk.text_classification.models import TextClassificationBulkData
from tests.server.test_helpers import client


@pytest.fixture
def sdk_client():
    return AuthenticatedClient(base_url="http://localhost:6900", token=DEFAULT_API_KEY)


@pytest.fixture
def bulk_data():
    return TextClassificationBulkData(
        records=[CreationTextClassificationRecord(inputs={"text": "test"})]
    )


def test_bulk(sdk_client, bulk_data, monkeypatch):
    monkeypatch.setattr(httpx, "post", client.post)

    dataset_name = "test_dataset"
    client.delete(f"/api/datasets/{dataset_name}")
    response = bulk(sdk_client, name=dataset_name, json_body=bulk_data)

    assert response.status_code == 200
