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

from uuid import uuid4

import httpx
from argilla_v1.client.sdk.v1.vectors_settings.api import delete_vector_settings, update_vector_settings


class TestSuiteVectorsSettingsSDK:
    def test_update_vector_settings(self, mock_httpx_client: httpx.Client) -> None:
        vector_settings_id = uuid4()
        mock_httpx_client.patch.return_value = httpx.Response(
            status_code=200,
            json={
                "id": str(vector_settings_id),
                "name": "vector-settings",
                "title": "new-title",
                "dimensions": 128,
                "dataset_id": str(uuid4()),
                "inserted_at": "2021-09-13T12:00:00Z",
                "updated_at": "2021-09-13T12:00:00Z",
            },
        )
        response = update_vector_settings(client=mock_httpx_client, id=vector_settings_id, title="new-title")
        assert response.status_code == 200
        assert response.parsed.title == "new-title"
        assert mock_httpx_client.patch.called_once_with(
            url=f"/api/v1/vectors-settings/{vector_settings_id}",
            json={"title": "new-title"},
        )

    def test_delete_vector_settings(self, mock_httpx_client: httpx.Client) -> None:
        vector_settings_id = uuid4()
        mock_httpx_client.delete.return_value = httpx.Response(
            status_code=200,
            json={
                "id": str(vector_settings_id),
                "name": "vector-settings",
                "title": "title",
                "dimensions": 128,
                "dataset_id": str(uuid4()),
                "inserted_at": "2021-09-13T12:00:00Z",
                "updated_at": "2021-09-13T12:00:00Z",
            },
        )
        response = delete_vector_settings(client=mock_httpx_client, id=vector_settings_id)
        assert response.status_code == 200
        assert mock_httpx_client.patch.called_once_with(url=f"/api/v1/vectors-settings/{vector_settings_id}")
