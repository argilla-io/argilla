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

import uuid

import httpx
from argilla_v1.client.sdk.v1.datasets.api import get_records


class TestSuiteGetRecordsSDK:
    def test_get_records_with_include_params(self, mock_httpx_client: httpx.Client):
        dataset_id = uuid.uuid4()
        limit = 5

        mock_httpx_client.get.return_value = httpx.Response(status_code=200, json={"total": 0, "items": []})

        get_records(
            client=mock_httpx_client,
            id=dataset_id,
            limit=limit,
            include=["metadata", "responses", "vectors:v1"],
        )

        mock_httpx_client.get.assert_called_once_with(
            url=f"/api/v1/datasets/{dataset_id}/records",
            params={"include": ["metadata", "responses", "vectors:v1"], "offset": 0, "limit": limit},
        )
