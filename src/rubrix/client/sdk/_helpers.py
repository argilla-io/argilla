from typing import Any, Dict, Type, TypeVar, Union

import httpx

from rubrix.client.sdk.commons.errors_handler import handle_response_error
from rubrix.client.sdk.commons.models import ErrorMessage, HTTPValidationError, Response


def build_raw_response(
    response: httpx.Response,
) -> Response[Union[Dict[str, Any], ErrorMessage, HTTPValidationError]]:
    return build_typed_response(response, response_type_class=dict)


ResponseType = TypeVar("ResponseType")


def build_typed_response(
    response: httpx.Response,
    response_type_class: Type[ResponseType],
) -> Response[Union[ResponseType, ErrorMessage, HTTPValidationError]]:
    parsed_response = response.json()

    check_response_error(response, expected_response=response_type_class)
    parsed_response = response_type_class(**parsed_response)
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=parsed_response,
    )


def check_response_error(response: httpx.Response, **kwargs) -> bool:
    if 200 <= response.status_code < 400:
        return False
    handle_response_error(response, **kwargs)
