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
from argilla_v1.client.sdk.v1.metadata_properties.api import update_metadata_property


class TestSuiteMetadataPropertiesSDK:
    def test_update_metadata_property(self, mock_httpx_client: httpx.Client) -> None:
        metadata_property_id = uuid4()
        mock_httpx_client.patch.return_value = httpx.Response(
            status_code=200,
            json={
                "id": str(metadata_property_id),
                "name": "metadata-property",
                "title": "new-title",
                "visible_for_annotators": False,
                "settings": {
                    "type": "terms",
                    "terms": ["term-1", "term-2"],
                },
                "inserted_at": "2021-09-13T12:00:00Z",
                "updated_at": "2021-09-13T12:00:00Z",
            },
        )

        response = update_metadata_property(
            client=mock_httpx_client, id=metadata_property_id, title="new-title", visible_for_annotators=False
        )

        assert response.status_code == 200
        assert response.parsed.title == "new-title"
        assert response.parsed.visible_for_annotators == False

        mock_httpx_client.patch.assert_called_once_with(
            url=f"/api/v1/metadata-properties/{metadata_property_id}",
            json={"title": "new-title", "visible_for_annotators": False},
        )
