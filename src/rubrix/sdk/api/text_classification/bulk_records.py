from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.bulk_response import BulkResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.text_classification_bulk_data import TextClassificationBulkData
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: TextClassificationBulkData,
) -> Dict[str, Any]:
    url = "{}/api/datasets/{name}/TextClassification/:bulk".format(
        client.base_url, name=name
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[BulkResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = BulkResponse.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[BulkResponse, HTTPValidationError]]:
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
    json_body: TextClassificationBulkData,
) -> Response[Union[BulkResponse, HTTPValidationError]]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: TextClassificationBulkData,
) -> Optional[Union[BulkResponse, HTTPValidationError]]:
    """Includes a chunk of record data with provided dataset bulk information

    Parameters
    ----------
    name:
        The dataset name
    bulk:
        The bulk data
    datasets:
        The dataset service
    service:
        The dataset records service
    current_user:
        Current request user

    Returns
    -------

        Bulk response data"""

    return sync_detailed(
        client=client,
        name=name,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: TextClassificationBulkData,
) -> Response[Union[BulkResponse, HTTPValidationError]]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: TextClassificationBulkData,
) -> Optional[Union[BulkResponse, HTTPValidationError]]:
    """Includes a chunk of record data with provided dataset bulk information

    Parameters
    ----------
    name:
        The dataset name
    bulk:
        The bulk data
    datasets:
        The dataset service
    service:
        The dataset records service
    current_user:
        Current request user

    Returns
    -------

        Bulk response data"""

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            json_body=json_body,
        )
    ).parsed
