#  coding=utf-8
#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.api_status import ApiStatus
from ...models.error_message import ErrorMessage
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


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[ApiStatus, ErrorMessage, ErrorMessage]]:
    if response.status_code == 200:
        response_200 = ApiStatus.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = ErrorMessage.from_dict(response.json())

        return response_404
    if response.status_code == 500:
        response_500 = ErrorMessage.from_dict(response.json())

        return response_500
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[ApiStatus, ErrorMessage, ErrorMessage]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Union[ApiStatus, ErrorMessage, ErrorMessage]]:
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
) -> Optional[Union[ApiStatus, ErrorMessage, ErrorMessage]]:
    """Parameters
    ----------
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
) -> Response[Union[ApiStatus, ErrorMessage, ErrorMessage]]:
    kwargs = _get_kwargs(
        client=client,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ApiStatus, ErrorMessage, ErrorMessage]]:
    """Parameters
    ----------
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
