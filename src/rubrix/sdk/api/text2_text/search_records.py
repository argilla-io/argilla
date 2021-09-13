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
from ...models.error_message import ErrorMessage
from ...models.http_validation_error import HTTPValidationError
from ...models.text2_text_search_request import Text2TextSearchRequest
from ...models.text2_text_search_results import Text2TextSearchResults
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: Text2TextSearchRequest,
    limit: Union[Unset, int] = 50,
    from_: Union[Unset, int] = 0,
) -> Dict[str, Any]:
    url = "{}/api/datasets/{name}/Text2Text:search".format(client.base_url, name=name)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "limit": limit,
        "from": from_,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[
    Union[Text2TextSearchResults, ErrorMessage, ErrorMessage, HTTPValidationError]
]:
    if response.status_code == 200:
        response_200 = Text2TextSearchResults.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = ErrorMessage.from_dict(response.json())

        return response_404
    if response.status_code == 500:
        response_500 = ErrorMessage.from_dict(response.json())

        return response_500
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[
    Union[Text2TextSearchResults, ErrorMessage, ErrorMessage, HTTPValidationError]
]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: Text2TextSearchRequest,
    limit: Union[Unset, int] = 50,
    from_: Union[Unset, int] = 0,
) -> Response[
    Union[Text2TextSearchResults, ErrorMessage, ErrorMessage, HTTPValidationError]
]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
        json_body=json_body,
        limit=limit,
        from_=from_,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: Text2TextSearchRequest,
    limit: Union[Unset, int] = 50,
    from_: Union[Unset, int] = 0,
) -> Optional[
    Union[Text2TextSearchResults, ErrorMessage, ErrorMessage, HTTPValidationError]
]:
    """Searches data from dataset

    Parameters
    ----------
    name:
        The dataset name
    search:
        THe search query request
    pagination:
        The pagination params
    service:
        The dataset records service
    datasets:
        The dataset service
    current_user:
        The current request user

    Returns
    -------
        The search results data"""

    return sync_detailed(
        client=client,
        name=name,
        json_body=json_body,
        limit=limit,
        from_=from_,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: Text2TextSearchRequest,
    limit: Union[Unset, int] = 50,
    from_: Union[Unset, int] = 0,
) -> Response[
    Union[Text2TextSearchResults, ErrorMessage, ErrorMessage, HTTPValidationError]
]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
        json_body=json_body,
        limit=limit,
        from_=from_,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: Text2TextSearchRequest,
    limit: Union[Unset, int] = 50,
    from_: Union[Unset, int] = 0,
) -> Optional[
    Union[Text2TextSearchResults, ErrorMessage, ErrorMessage, HTTPValidationError]
]:
    """Searches data from dataset

    Parameters
    ----------
    name:
        The dataset name
    search:
        THe search query request
    pagination:
        The pagination params
    service:
        The dataset records service
    datasets:
        The dataset service
    current_user:
        The current request user

    Returns
    -------
        The search results data"""

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            json_body=json_body,
            limit=limit,
            from_=from_,
        )
    ).parsed
