from typing import Any, Dict, Optional

import httpx

from ...client import AuthenticatedClient
from ...models.api_status import ApiStatus
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/api/_status".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[ApiStatus]:
    if response.status_code == 200:
        response_200 = ApiStatus.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[ApiStatus]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[ApiStatus]:
    kwargs = _get_kwargs(
        client=client,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Optional[ApiStatus]:
    """Parameters
    ----------
    current_user:
        Connected user (since protected endpoint)
    service:
        The Api info service

    Returns
    -------

    The detailed api status"""

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[ApiStatus]:
    kwargs = _get_kwargs(
        client=client,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[ApiStatus]:
    """Parameters
    ----------
    current_user:
        Connected user (since protected endpoint)
    service:
        The Api info service

    Returns
    -------

    The detailed api status"""

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
