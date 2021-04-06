import json
from typing import Any, Dict, Optional, Union

import httpx
from rubrix.sdk.models import ErrorMessage

from ...client import AuthenticatedClient
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    name: str,
) -> Dict[str, Any]:
    url = "{}/api/datasets/{name}/TokenClassification/data".format(
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


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[None, HTTPValidationError, ErrorMessage]]:
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
) -> Response[Union[None, HTTPValidationError]]:
    parse_response = _parse_response(response=response)
    if not parse_response:
        parse_response = [json.loads(r) for r in response.iter_lines()]
    return Response(
        status_code=response.status_code,
        content=b"",
        headers=response.headers,
        parsed=parse_response,
    )


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
        return _build_response(response=response)


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
