import pytest

from rubrix.client import api
from rubrix.client.apis import AbstractApi, api_compatibility
from rubrix.client.sdk._helpers import handle_response_error
from rubrix.client.sdk.commons.errors import ApiCompatibilityError


def test_api_compatibility(mocked_client):
    client = api.active_api().client
    dummy_api = AbstractApi(client)
    with pytest.raises(ApiCompatibilityError):
        with api_compatibility(api=dummy_api, min_version="1.0"):
            handle_response_error(mocked_client.post("/api/datasets"))
