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

import logging

import pydantic

from argilla.server.errors.base_errors import (
    BadRequestError,
    GenericServerError,
    ServerError,
    ValidationError,
)

_LOGGER = logging.getLogger("argilla")


def exception_to_argilla_error(error: Exception) -> ServerError:
    if isinstance(error, ServerError):
        return error
    _LOGGER.error(error)
    if isinstance(error, pydantic.error_wrappers.ValidationError):
        return ValidationError(error)

    if isinstance(error, AssertionError):
        return BadRequestError(str(error))

    # TODO: here we can extend/specify more error adapters
    return GenericServerError(error=error)
