from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.dataset import Dataset
from ...models.error_message import ErrorMessage
from ...models.http_validation_error import HTTPValidationError
from ...models.update_dataset_request import UpdateDatasetRequest
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: UpdateDatasetRequest,
) -> Dict[str, Any]:
    url = "{}/api/datasets/{name}".format(client.base_url, name=name)

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
) -> Optional[Union[Dataset, ErrorMessage, ErrorMessage, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = Dataset.from_dict(response.json())

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
) -> Response[Union[Dataset, ErrorMessage, ErrorMessage, HTTPValidationError]]:
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
    json_body: UpdateDatasetRequest,
) -> Response[Union[Dataset, ErrorMessage, ErrorMessage, HTTPValidationError]]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
        json_body=json_body,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: UpdateDatasetRequest,
) -> Optional[Union[Dataset, ErrorMessage, ErrorMessage, HTTPValidationError]]:
    """Update a set of parameters for a dataset

    Parameters
    ----------
    name:
        The dataset name
    update_request:
        The fields to update
    service:
        The datasets service
    current_user:
        The current user

    Returns
    -------

    - The updated dataset if exists and user has access.
    - EntityNotFoundError if not found.
    - NotAuthorizedError if user cannot access the found dataset"""

    return sync_detailed(
        client=client,
        name=name,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: UpdateDatasetRequest,
) -> Response[Union[Dataset, ErrorMessage, ErrorMessage, HTTPValidationError]]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: UpdateDatasetRequest,
) -> Optional[Union[Dataset, ErrorMessage, ErrorMessage, HTTPValidationError]]:
    """Update a set of parameters for a dataset

    Parameters
    ----------
    name:
        The dataset name
    update_request:
        The fields to update
    service:
        The datasets service
    current_user:
        The current user

    Returns
    -------

    - The updated dataset if exists and user has access.
    - EntityNotFoundError if not found.
    - NotAuthorizedError if user cannot access the found dataset"""

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            json_body=json_body,
        )
    ).parsed
