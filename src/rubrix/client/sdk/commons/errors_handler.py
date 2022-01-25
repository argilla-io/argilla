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
    response: httpx.Response, parse_response: bool = True, **extra_args
):
    try:
        response_content = response.json() if parse_response else {}
    except JSONDecodeError:
        response_content = {}

    if response.status_code == BadRequestApiError.HTTP_STATUS:
        raise BadRequestApiError(**response_content, **extra_args)
    if response.status_code == UnauthorizedApiError.HTTP_STATUS:
        raise UnauthorizedApiError(**response_content, **extra_args)
    if response.status_code == AlreadyExistsApiError.HTTP_STATUS:
        raise AlreadyExistsApiError(**response_content, **extra_args)
    if response.status_code == ForbiddenApiError.HTTP_STATUS:
        raise ForbiddenApiError(**response_content, **extra_args)
    if response.status_code == NotFoundApiError.HTTP_STATUS:
        raise NotFoundApiError(**response_content, **extra_args)
    if response.status_code == ValidationApiError.HTTP_STATUS:
        raise ValidationApiError(**response_content, **extra_args)
    raise GenericApiError(**response_content)
