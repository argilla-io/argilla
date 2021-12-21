import httpx

from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.models import ErrorMessage, HTTPValidationError, Response
from rubrix.client.sdk.users.models import User


def _parse_response(response: httpx.Response):
    parsed_response = None
    if response.status_code == 200:
        parsed_response = User(**response.json())
    elif response.status_code == 404:
        parsed_response = ErrorMessage(**response.json())
    elif response.status_code == 500:
        parsed_response = ErrorMessage(**response.json())
    elif response.status_code == 422:
        parsed_response = HTTPValidationError(**response.json())

    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=parsed_response,
    )


def whoami(client: AuthenticatedClient):
    url = "{}/api/me".format(client.base_url)

    response = httpx.get(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
    )

    return _parse_response(response)
