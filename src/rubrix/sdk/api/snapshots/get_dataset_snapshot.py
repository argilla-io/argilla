from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.dataset_snapshot import DatasetSnapshot
from ...models.error_message import ErrorMessage
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    name: str,
    snapshot_id: str,
) -> Dict[str, Any]:
    url = "{}/api/datasets/{name}/snapshots/{snapshot_id}".format(
        client.base_url, name=name, snapshot_id=snapshot_id
    )

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
) -> Optional[Union[DatasetSnapshot, ErrorMessage, ErrorMessage, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = DatasetSnapshot.from_dict(response.json())

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
) -> Response[Union[DatasetSnapshot, ErrorMessage, ErrorMessage, HTTPValidationError]]:
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
    snapshot_id: str,
) -> Response[Union[DatasetSnapshot, ErrorMessage, ErrorMessage, HTTPValidationError]]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
        snapshot_id=snapshot_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    name: str,
    snapshot_id: str,
) -> Optional[Union[DatasetSnapshot, ErrorMessage, ErrorMessage, HTTPValidationError]]:
    """Get snapshot by id

    Parameters
    ----------
    name:
        Dataset name
    snapshot_id:
        Snapshot id
    service:
        Snapshots service
    current_user:
        Current request user

    Returns
    -------
        Found snapshot"""

    return sync_detailed(
        client=client,
        name=name,
        snapshot_id=snapshot_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    name: str,
    snapshot_id: str,
) -> Response[Union[DatasetSnapshot, ErrorMessage, ErrorMessage, HTTPValidationError]]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
        snapshot_id=snapshot_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    name: str,
    snapshot_id: str,
) -> Optional[Union[DatasetSnapshot, ErrorMessage, ErrorMessage, HTTPValidationError]]:
    """Get snapshot by id

    Parameters
    ----------
    name:
        Dataset name
    snapshot_id:
        Snapshot id
    service:
        Snapshots service
    current_user:
        Current request user

    Returns
    -------
        Found snapshot"""

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            snapshot_id=snapshot_id,
        )
    ).parsed
