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
from typing import List, Type, TypeVar, Union

import httpx

from rubrix.client.sdk.commons.models import (
    BulkResponse,
    ErrorMessage,
    HTTPValidationError,
    Response,
)


def build_bulk_response(
    response: httpx.Response,
) -> Response[Union[BulkResponse, ErrorMessage, HTTPValidationError]]:

    parsed_response = None
    if response.status_code == 200:
        parsed_response = BulkResponse(**response.json())
    elif response.status_code == 404:
        parsed_response = ErrorMessage(**response.json())
    elif response.status_code == 500:
        parsed_response = ErrorMessage(**response.json())
    elif response.status_code == 422:
        parsed_response = HTTPValidationError(**response.json())

    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=parsed_response,
    )


T = TypeVar("T")


def build_data_response(
    response: httpx.Response, data_type: Type[T]
) -> Response[Union[List[T], HTTPValidationError, ErrorMessage]]:
    if 200 <= response.status_code < 400:
        parsed_response = [data_type(**json.loads(r)) for r in response.iter_lines()]
    else:
        content = next(response.iter_lines())
        data = json.loads(content)
        parsed_response = (
            HTTPValidationError(**data)
            if response.status_code == 422
            else ErrorMessage(**data)
        )

    return Response(
        status_code=response.status_code,
        content=b"",
        headers=response.headers,
        parsed=parsed_response,
    )
