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
from rubrix.client.sdk.datasets.models import Dataset
from rubrix.client.sdk.text_classification.models import TextClassificationBulkData
from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.datasets.api import get_dataset
from tests.server.test_helpers import client


@pytest.fixture
def sdk_client():
    return AuthenticatedClient(base_url="http://localhost:6900", token=DEFAULT_API_KEY)


def test_get_dataset(create_empty_text_classification_test_dataset, sdk_client, monkeypatch):
    monkeypatch.setattr(httpx, "get", client.get)

    # create test dataset
    bulk_data = TextClassificationBulkData(records=[])
    dataset_name = "test_dataset"
    client.delete(f"/api/datasets/{dataset_name}")
    client.post(
        f"/api/datasets/{dataset_name}/TextClassification:bulk",
        json=bulk_data.dict(by_alias=True),
    )

    response = get_dataset(client=sdk_client, name="test_dataset")

    assert response.status_code == 200
    assert isinstance(response.parsed, Dataset)
