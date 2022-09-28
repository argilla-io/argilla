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

import httpx

from argilla.client.sdk.commons.errors import (
    AlreadyExistsApiError,
    BadRequestApiError,
    ForbiddenApiError,
    GenericApiError,
    MethodNotAllowedApiError,
    NotFoundApiError,
    UnauthorizedApiError,
    ValidationApiError,
)


def handle_response_error(
    response: httpx.Response, parse_response: bool = True, **client_ctx
):
    try:
        response_content = response.json() if parse_response else {}
    except JSONDecodeError:
        response_content = {}
    error_type = GenericApiError
    error_detail = response_content.get("detail")
    if not isinstance(error_detail, dict):  # normalize detail if not data structure
        error_detail = {"response": error_detail}

    error_args = error_detail if error_detail else response_content

    if response.status_code == BadRequestApiError.HTTP_STATUS:
        error_type = BadRequestApiError
    elif response.status_code == UnauthorizedApiError.HTTP_STATUS:
        error_type = UnauthorizedApiError
    elif response.status_code == AlreadyExistsApiError.HTTP_STATUS:
        error_type = AlreadyExistsApiError
    elif response.status_code == ForbiddenApiError.HTTP_STATUS:
        error_type = ForbiddenApiError
    elif response.status_code == NotFoundApiError.HTTP_STATUS:
        error_type = NotFoundApiError
    elif response.status_code == ValidationApiError.HTTP_STATUS:
        error_type = ValidationApiError
        error_args["client_ctx"] = client_ctx
    elif response.status_code == MethodNotAllowedApiError.HTTP_STATUS:
        error_type = MethodNotAllowedApiError

    raise error_type(**error_args)
