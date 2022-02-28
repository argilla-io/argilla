import httpx
import pytest

from rubrix import DEFAULT_API_KEY
from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.errors import UnauthorizedApiError
from rubrix.client.sdk.users.api import whoami
from rubrix.client.sdk.users.models import User


def test_whoami(mocked_client):
    sdk_client = AuthenticatedClient(
        base_url="http://localhost:6900", token=DEFAULT_API_KEY
    )
    user = whoami(client=sdk_client)
    assert isinstance(user, User)


def test_whoami_with_auth_error(mocked_client):
    with pytest.raises(UnauthorizedApiError):
        whoami(
            AuthenticatedClient(base_url="http://localhost:6900", token="wrong-apikey")
        )


def test_whoami_with_connection_error():
    with pytest.raises(httpx.ConnectError):
        whoami(
            AuthenticatedClient(base_url="http://localhost:6900", token="wrong-apikey")
        )
