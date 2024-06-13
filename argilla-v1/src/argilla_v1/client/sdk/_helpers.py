#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from json import JSONDecodeError
from typing import Any, Dict, Optional, Type, TypeVar, Union

import httpx

from argilla_v1.client.sdk.commons.errors import WrongResponseError
from argilla_v1.client.sdk.commons.errors_handler import handle_response_error
from argilla_v1.client.sdk.commons.models import ErrorMessage, HTTPValidationError, Response


def build_raw_response(response: httpx.Response) -> Response[Union[Dict[str, Any], ErrorMessage, HTTPValidationError]]:
    return build_typed_response(response)


ResponseType = TypeVar("ResponseType")


def build_typed_response(
    response: httpx.Response, response_type_class: Optional[Type[ResponseType]] = None
) -> Response[Union[ResponseType, ErrorMessage, HTTPValidationError]]:
    parsed_response = check_response(response, expected_response=response_type_class)
    if response_type_class:
        parsed_response = response_type_class(**parsed_response)
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=parsed_response,
    )


def check_response(response: httpx.Response, **kwargs) -> Any:
    if 200 <= response.status_code < 300:
        try:
            return response.json()
        except JSONDecodeError:
            raise WrongResponseError(
                message="Cannot parse json data from response",
                response=response.content,
            )
    if 300 <= response.status_code < 400:
        message = (
            f"Unexpected response {response.status_code} status. "
            "Verify your client/server connection and retry the operation"
        )
        raise WrongResponseError(
            message=message,
            response=response.content,
        )
    handle_response_error(response, **kwargs)
