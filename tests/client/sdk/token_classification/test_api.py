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

from rubrix.client.sdk.token_classification.api import data
from rubrix.client.sdk.token_classification.models import TokenClassificationRecord


@pytest.mark.parametrize("limit,expected", [(None, 3), (2, 2)])
def test_data(
    mocked_client, limit, expected, sdk_client, bulk_tokenclass_data, monkeypatch
):

    dataset_name = "test_dataset"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    mocked_client.post(
        f"/api/datasets/{dataset_name}/TokenClassification:bulk",
        json=bulk_tokenclass_data.dict(by_alias=True),
    )

    response = data(sdk_client, name=dataset_name, limit=limit)
    assert isinstance(response.parsed[0], TokenClassificationRecord)
    assert len(response.parsed) == expected
