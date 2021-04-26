from typing import Any, Dict, Optional, Union

import httpx
from rubrix.sdk.api._streaming_helpers import build_stream_response
from rubrix.sdk.models import TextClassificationQuery

from ...client import AuthenticatedClient
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    name: str,
    json_body: Optional[TextClassificationQuery] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    url = "{}/api/datasets/{name}/TextClassification/data".format(
        client.base_url, name=name
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params = {"limit": limit}
    params = {k: v for k, v in params.items() if v is not None}

    json_json_body = json_body.to_dict() if json_body else {}
    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": None,
        "params": params,
        "json": json_json_body,
    }


def sync_detailed(
    *,
    client: AuthenticatedClient,
    name: str,
    request: Optional[TextClassificationQuery] = None,
    limit: Optional[int] = None,
) -> Response[Union[None, HTTPValidationError]]:
    kwargs = _get_kwargs(client=client, name=name, limit=limit, json_body=request)

    with httpx.stream("POST", **kwargs) as response:
        return build_stream_response(response=response)
