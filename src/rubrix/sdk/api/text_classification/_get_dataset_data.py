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
) -> Dict[str, Any]:
    url = "{}/api/datasets/{name}/TextClassification/data".format(
        client.base_url, name=name
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": None,
    }


def sync_detailed(
    *,
    client: AuthenticatedClient,
    name: str,
) -> Response[Union[None, HTTPValidationError]]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
    )

    with httpx.stream("GET", **kwargs) as response:
        return build_stream_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    name: str,
) -> Optional[Union[None, HTTPValidationError]]:
    """Creates a data stream over dataset records

    Parameters
    ----------
    name
        The dataset name
    """
    return sync_detailed(
        client=client,
        name=name,
    ).parsed
