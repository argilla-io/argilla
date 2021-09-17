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
from attr import asdict

from ...client import Client
from ...models.body_login_for_access_token_api_security_token_post import (
    BodyLoginForAccessTokenApiSecurityTokenPost,
)
from ...models.http_validation_error import HTTPValidationError
from ...models.token import Token
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    form_data: BodyLoginForAccessTokenApiSecurityTokenPost,
) -> Dict[str, Any]:
    url = "{}/api/security/token".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "data": asdict(form_data),
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[Token, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = Token.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[Token, HTTPValidationError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    form_data: BodyLoginForAccessTokenApiSecurityTokenPost,
) -> Response[Union[Token, HTTPValidationError]]:
    kwargs = _get_kwargs(
        client=client,
        form_data=form_data,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    form_data: BodyLoginForAccessTokenApiSecurityTokenPost,
) -> Optional[Union[Token, HTTPValidationError]]:
    """Login access token api endpoint

    Parameters
    ----------
    form_data:
        The user/password form

    Returns
    -------
        Logging token if user is properly authenticated.
        Unauthorized exception otherwise"""

    return sync_detailed(
        client=client,
        form_data=form_data,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    form_data: BodyLoginForAccessTokenApiSecurityTokenPost,
) -> Response[Union[Token, HTTPValidationError]]:
    kwargs = _get_kwargs(
        client=client,
        form_data=form_data,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    form_data: BodyLoginForAccessTokenApiSecurityTokenPost,
) -> Optional[Union[Token, HTTPValidationError]]:
    """Login access token api endpoint

    Parameters
    ----------
    form_data:
        The user/password form

    Returns
    -------
        Logging token if user is properly authenticated.
        Unauthorized exception otherwise"""

    return (
        await asyncio_detailed(
            client=client,
            form_data=form_data,
        )
    ).parsed
