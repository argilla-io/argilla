from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.error_message import ErrorMessage
from ...models.http_validation_error import HTTPValidationError
from ...models.text_classification_search_request import TextClassificationSearchRequest
from ...models.text_classification_search_results import TextClassificationSearchResults
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: TextClassificationSearchRequest,
    limit: Union[Unset, int] = 50,
    from_: Union[Unset, int] = 0,
) -> Dict[str, Any]:
    url = "{}/api/datasets/{name}/TextClassification:search".format(
        client.base_url, name=name
    )

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
    Union[
        TextClassificationSearchResults, ErrorMessage, ErrorMessage, HTTPValidationError
    ]
]:
    if response.status_code == 200:
        response_200 = TextClassificationSearchResults.from_dict(response.json())

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
    Union[
        TextClassificationSearchResults, ErrorMessage, ErrorMessage, HTTPValidationError
    ]
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
    json_body: TextClassificationSearchRequest,
    limit: Union[Unset, int] = 50,
    from_: Union[Unset, int] = 0,
) -> Response[
    Union[
        TextClassificationSearchResults, ErrorMessage, ErrorMessage, HTTPValidationError
    ]
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
    json_body: TextClassificationSearchRequest,
    limit: Union[Unset, int] = 50,
    from_: Union[Unset, int] = 0,
) -> Optional[
    Union[
        TextClassificationSearchResults, ErrorMessage, ErrorMessage, HTTPValidationError
    ]
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
    json_body: TextClassificationSearchRequest,
    limit: Union[Unset, int] = 50,
    from_: Union[Unset, int] = 0,
) -> Response[
    Union[
        TextClassificationSearchResults, ErrorMessage, ErrorMessage, HTTPValidationError
    ]
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
    json_body: TextClassificationSearchRequest,
    limit: Union[Unset, int] = 50,
    from_: Union[Unset, int] = 0,
) -> Optional[
    Union[
        TextClassificationSearchResults, ErrorMessage, ErrorMessage, HTTPValidationError
    ]
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
