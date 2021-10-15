import httpx
import pytest

from rubrix import DEFAULT_API_KEY
from rubrix.client import AuthenticatedClient, whoami
from rubrix.client.sdk.users.models import User

from tests.server.test_helpers import client


@pytest.fixture
def sdk_client():
    return AuthenticatedClient(base_url="http://localhost:6900", token=DEFAULT_API_KEY)


def test_whoami(sdk_client, monkeypatch):
    monkeypatch.setattr(httpx, "get", client.get)

    response = whoami(client=sdk_client)

    assert response.status_code == 200
    assert isinstance(response.parsed, User)
