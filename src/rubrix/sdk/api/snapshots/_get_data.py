import json
from typing import Any, Dict, Optional, Union

import httpx
from rubrix.sdk.api._streaming_helpers import build_stream_response
from rubrix.sdk.models import ErrorMessage

from ...client import AuthenticatedClient
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    name: str,
    snapshot_id: str,
) -> Dict[str, Any]:
    url = "{}/api/datasets/{name}/snapshots/{snapshot_id}/data".format(
        client.base_url, name=name, snapshot_id=snapshot_id
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": None,  # Override default timeout
    }


def sync_detailed(
    *,
    client: AuthenticatedClient,
    name: str,
    snapshot_id: str,
) -> Response[Union[None, HTTPValidationError]]:
    kwargs = _get_kwargs(client=client, name=name, snapshot_id=snapshot_id)

    with httpx.stream("GET", **kwargs) as response:
        return build_stream_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    name: str,
    snapshot_id: str,
) -> Optional[Union[None, HTTPValidationError]]:
    """Creates a data stream over dataset snapshot records

    Parameters
    ----------
    name
        The dataset name
    snapshot_id:
        The dataset snapshot id
    """

    return sync_detailed(client=client, name=name, snapshot_id=snapshot_id).parsed
