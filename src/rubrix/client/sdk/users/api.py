import httpx

from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.errors_handler import handle_response_error
from rubrix.client.sdk.users.models import User


def whoami(client: AuthenticatedClient) -> User:
    url = "{}/api/me".format(client.base_url)
    try:
        response = httpx.get(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
        )

        if response.status_code == 200:
            return User(**response.json())

        handle_response_error(response, msg="Invalid credentials")
    except httpx.ConnectError as err:
        raise Exception(f"Could not connect to api_url:{client.base_url}") from None
