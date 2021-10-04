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
from typing import Union, Optional

import httpx
from rubrix.client.sdk.commons.models import BulkResponse
from rubrix.client.sdk.commons.models import ErrorMessage
from rubrix.client.sdk.commons.models import HTTPValidationError
from rubrix.client.sdk.commons.models import Response


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
