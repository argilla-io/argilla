import logging

import pydantic

from rubrix.server.commons.errors.base_errors import (
    BadRequestError,
    GenericRubrixServerError,
    RubrixServerError,
    ValidationError,
)

_LOGGER = logging.getLogger("rubrix")


def exception_to_rubrix_error(error: Exception) -> RubrixServerError:
    if isinstance(error, RubrixServerError):
        return error
    _LOGGER.error(error)
    if isinstance(error, pydantic.error_wrappers.ValidationError):
        return ValidationError(error)

    if isinstance(error, AssertionError):
        return BadRequestError(str(error))

    # TODO: here we can extend/specify more error adapters
    return GenericRubrixServerError(error=error)
