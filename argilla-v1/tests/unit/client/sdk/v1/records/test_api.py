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

from datetime import datetime
from uuid import uuid4

import httpx
from argilla_v1.client.sdk.v1.records.api import update_record


class TestSuiteRecordsSDK:
    def test_update_record_with_vectors(self, mock_httpx_client: httpx.Client) -> None:
        record_id = uuid4()
        mock_httpx_client.patch.return_value = httpx.Response(
            status_code=200,
            json={
                "id": str(record_id),
                "fields": {"text": "Text"},
                "vectors": {
                    "vector-1": [1.0, 2.0, 3.0],
                    "vector-2": [1.0, 2.0, 3.0, 4.0],
                },
                "inserted_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        response = update_record(
            client=mock_httpx_client,
            id=record_id,
            data={
                "vectors": {
                    "vector-1": [1.0, 2.0, 3.0],
                    "vector-2": [1.0, 2.0, 3.0, 4.0],
                }
            },
        )

        assert response.status_code == 200
        assert response.parsed.vectors == {
            "vector-1": [1.0, 2.0, 3.0],
            "vector-2": [1.0, 2.0, 3.0, 4.0],
        }

        mock_httpx_client.patch.assert_called_once_with(
            url=f"/api/v1/records/{record_id}",
            json={
                "vectors": {
                    "vector-1": [1.0, 2.0, 3.0],
                    "vector-2": [1.0, 2.0, 3.0, 4.0],
                }
            },
        )
