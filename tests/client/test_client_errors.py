import pytest

from rubrix.client.sdk.commons.errors import UnauthorizedApiError


def test_unauthorized_response_error(mocked_client):

    with pytest.raises(UnauthorizedApiError, match="Could not validate credentials"):
        import rubrix as rb

        rb.init(api_key="wrong-api-key")
