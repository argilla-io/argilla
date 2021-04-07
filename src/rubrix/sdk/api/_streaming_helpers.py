from typing import Iterable, Optional, Union

try:
    import ujson as json
except ModuleNotFoundError:
    import json
import httpx
from rubrix.sdk.models import ErrorMessage, HTTPValidationError
from rubrix.sdk.types import Response


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[None, HTTPValidationError, ErrorMessage]]:
    if 200 <= response.status_code < 400:
        return None

    content = next(response.iter_lines())
    data = json.loads(content)
    if response.status_code == 422:
        return HTTPValidationError.from_dict(data)
    return ErrorMessage.from_dict(data)


def build_stream_response(
    response: httpx.Response,
) -> Response[Union[Iterable, HTTPValidationError, ErrorMessage]]:
    """
    Build a response from stream response

    Parameters
    ----------
    response:
        The stream response

    Returns
    -------
    A stream response with iterable data content
    """
    parse_response = _parse_response(response=response)
    if not parse_response:
        parse_response = [json.loads(r) for r in response.iter_lines()]
    return Response(
        status_code=response.status_code,
        content=b"",
        headers=response.headers,
        parsed=parse_response,
    )
