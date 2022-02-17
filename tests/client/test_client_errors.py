import pytest

from rubrix.client.sdk.commons.errors import UnauthorizedApiError
from tests.server.test_helpers import client, mocking_client


def test_unauthorized_response_error(monkeypatch):
    mocking_client(monkeypatch, client)

    with pytest.raises(UnauthorizedApiError, match="Could not validate credentials"):
        import rubrix as rb

        rb.init(api_key="wrong-api-key")
