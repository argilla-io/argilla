import uuid

import httpx

from argilla.client.sdk.v1.datasets.api import get_records


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
