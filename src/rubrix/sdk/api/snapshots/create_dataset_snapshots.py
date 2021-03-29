from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient
from ...models.dataset_snapshot import DatasetSnapshot
from ...models.http_validation_error import HTTPValidationError
from ...models.task_type import TaskType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    name: str,
    task: Union[Unset, TaskType] = UNSET,
) -> Dict[str, Any]:
    url = "{}/api/datasets/{name}/snapshots".format(client.base_url, name=name)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_task: Union[Unset, TaskType] = UNSET
    if not isinstance(task, Unset):
        json_task = task

    params: Dict[str, Any] = {
        "task": json_task,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[DatasetSnapshot, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = DatasetSnapshot.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[DatasetSnapshot, HTTPValidationError]]:
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
    task: Union[Unset, TaskType] = UNSET,
) -> Response[Union[DatasetSnapshot, HTTPValidationError]]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
        task=task,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    name: str,
    task: Union[Unset, TaskType] = UNSET,
) -> Optional[Union[DatasetSnapshot, HTTPValidationError]]:
    """Creates a dataset snapshot

    Parameters
    ----------
    name:
        Dataset name
    task:
        Task type query selector
    service:
        Snapshots service
    current_user:
        Current request user

    Returns
    -------
        Created snapshot"""

    return sync_detailed(
        client=client,
        name=name,
        task=task,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    name: str,
    task: Union[Unset, TaskType] = UNSET,
) -> Response[Union[DatasetSnapshot, HTTPValidationError]]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
        task=task,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    name: str,
    task: Union[Unset, TaskType] = UNSET,
) -> Optional[Union[DatasetSnapshot, HTTPValidationError]]:
    """Creates a dataset snapshot

    Parameters
    ----------
    name:
        Dataset name
    task:
        Task type query selector
    service:
        Snapshots service
    current_user:
        Current request user

    Returns
    -------
        Created snapshot"""

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            task=task,
        )
    ).parsed
