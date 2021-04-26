from typing import Any, Dict, Optional, Union

import httpx
from rubrix.sdk.api._streaming_helpers import build_stream_response

from ...client import AuthenticatedClient
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    name: str,
    snapshot_id: str,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    url = "{}/api/datasets/{name}/snapshots/{snapshot_id}/data".format(
        client.base_url, name=name, snapshot_id=snapshot_id
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params = {"limit": limit}
    params = {k: v for k, v in params.items() if v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": None,  # Override default timeout
        "params": params,
    }


def sync_detailed(
    *,
    client: AuthenticatedClient,
    name: str,
    snapshot_id: str,
    limit: Optional[int] = None,
) -> Response[Union[None, HTTPValidationError]]:
    kwargs = _get_kwargs(client=client, name=name, snapshot_id=snapshot_id, limit=limit)

    with httpx.stream("GET", **kwargs) as response:
        return build_stream_response(response=response)
