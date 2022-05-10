import pytest

from rubrix.client.apis import api_compatibility
from rubrix.client.sdk._helpers import handle_response_error
from rubrix.client.sdk.commons.errors import ApiCompatibilityError


@pytest.mark.parametrize(
    "wrong_endpoint",
    ["/api/blabla", "/oco", "/api/datasets/", "/api/datasets/bolos/neu"],
)
def test_api_compatibility(mocked_client, wrong_endpoint):

    with pytest.raises(ApiCompatibilityError):
        with api_compatibility(min_version=(0, 15, 0)):
            handle_response_error(mocked_client.post(wrong_endpoint))
