import httpx

from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.errors_handler import handle_response_error
from rubrix.client.sdk.users.models import User


def whoami(client: AuthenticatedClient) -> User:
    response = client.get("/api/me")
    return User(**response)
