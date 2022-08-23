import httpx
import pytest

from rubrix._constants import DEFAULT_API_KEY
from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.errors import RubrixClientError, UnauthorizedApiError
from rubrix.client.sdk.users.api import whoami
from rubrix.client.sdk.users.models import User


def test_whoami(mocked_client, sdk_client):
    user = whoami(client=sdk_client)
    assert isinstance(user, User)


def test_whoami_with_auth_error(monkeypatch, mocked_client):
    with pytest.raises(UnauthorizedApiError):
        sdk_client = AuthenticatedClient(
            base_url="http://localhost:6900", token="wrong-apikey"
        )
        monkeypatch.setattr(sdk_client, "__httpx__", mocked_client)
        whoami(sdk_client)


def test_whoami_with_connection_error():
    with pytest.raises(RubrixClientError):
        whoami(
            AuthenticatedClient(base_url="http://localhost:6900", token="wrong-apikey")
        )
