from json import JSONDecodeError

import httpx

from rubrix.client.sdk.commons.errors import (
    AlreadyExistsApiError,
    BadRequestApiError,
    ForbiddenApiError,
    GenericApiError,
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
    if response.status_code == UnauthorizedApiError.HTTP_STATUS:
        error_type = UnauthorizedApiError
    if response.status_code == AlreadyExistsApiError.HTTP_STATUS:
        error_type = AlreadyExistsApiError
    if response.status_code == ForbiddenApiError.HTTP_STATUS:
        error_type = ForbiddenApiError
    if response.status_code == NotFoundApiError.HTTP_STATUS:
        error_type = NotFoundApiError
    if response.status_code == ValidationApiError.HTTP_STATUS:
        error_type = ValidationApiError

    if error_type == ValidationApiError:
        error_args["client_ctx"] = client_ctx

    raise error_type(**error_args)
