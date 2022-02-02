import httpx

from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.errors_handler import handle_response_error
from rubrix.client.sdk.commons.models import Response
from rubrix.client.sdk.users.models import User


def whoami(client: AuthenticatedClient):
    url = "{}/api/me".format(client.base_url)

    response = httpx.get(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
    )

    if response.status_code == 200:
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=User(**response.json()),
        )

    return handle_response_error(response, msg="Invalid credentials")
