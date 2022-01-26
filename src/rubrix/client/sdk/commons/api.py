#  coding=utf-8
#  coding=utf-8
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
import json
from typing import Any, Dict, List, Type, TypeVar, Union

import httpx

from rubrix.client.sdk.commons.errors_handler import handle_response_error
from rubrix.client.sdk.commons.models import (
    BulkResponse,
    ErrorMessage,
    HTTPValidationError,
    Response,
)


def build_bulk_response(
    response: httpx.Response, name: str, body: Any
) -> Response[BulkResponse]:

    if 200 <= response.status_code < 400:
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=BulkResponse(**response.json()),
        )

    return handle_response_error(response, name=name, body=body)


T = TypeVar("T")


def build_data_response(
    response: httpx.Response, data_type: Type[T]
) -> Response[List[T]]:
    if 200 <= response.status_code < 400:
        parsed_response = [data_type(**json.loads(r)) for r in response.iter_lines()]
        return Response(
            status_code=response.status_code,
            content=b"",
            headers=response.headers,
            parsed=parsed_response,
        )

    content = next(response.iter_lines())
    data = json.loads(content)
    return handle_response_error(response, **data, parse_response=False)


def build_list_response(
    response: httpx.Response,
    item_class: Type[T],
) -> Response[Union[List[T], HTTPValidationError, ErrorMessage]]:
    parsed_response = response.json()

    if 200 <= response.status_code < 400:
        parsed_response = [item_class(**r) for r in parsed_response]
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )

    return handle_response_error(response, item_class=item_class)


ResponseType = TypeVar("ResponseType")


def build_typed_response(
    response: httpx.Response,
    response_type_class: Type[ResponseType],
) -> Response[Union[ResponseType, ErrorMessage, HTTPValidationError]]:
    parsed_response = response.json()
    if 200 <= response.status_code < 400:
        parsed_response = response_type_class(**parsed_response)
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            parsed=parsed_response,
        )

    return handle_response_error(response, expected_response=response_type_class)


def build_raw_response(
    response: httpx.Response,
) -> Response[Union[Dict[str, Any], ErrorMessage, HTTPValidationError]]:
    return build_typed_response(response, response_type_class=dict)
