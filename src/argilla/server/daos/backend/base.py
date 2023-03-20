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

import dataclasses
import warnings
from abc import ABC
from typing import Any, List, Optional, Type

from pydantic import BaseModel

from argilla.server.errors import InvalidTextSearchError


class ClosedIndexError(Exception):
    pass


class IndexNotFoundError(Exception):
    pass


class InvalidSearchError(Exception):
    def __init__(self, origin_error: Exception):
        self.origin_error = origin_error


class WrongLogDataError(Exception):
    """Error on logging data"""

    class Error(BaseModel):
        reason: str = None
        caused_by: Any = None

    def __init__(self, errors: List[Error]):
        self.errors = errors


class GenericSearchError(Exception):
    def __init__(self, origin_error: Exception):
        self.origin_error = origin_error


@dataclasses.dataclass
class BackendErrorHandler(ABC):

    """Implements the error handler base class"""

    RequestError: Type[Exception]
    NotFoundError: Type[Exception]
    GenericApiError: Type[Exception]
    BulkError: Type[Exception]
    WarningIgnore: Type[Warning]

    def __call__(self, index: Optional[str] = None):
        ignore_warning = self.WarningIgnore
        request_error = self.RequestError
        bulk_error = self.BulkError
        not_found_error = self.NotFoundError
        generic_api_error = self.GenericApiError

        class _InnerContext:
            def __enter__(self):
                warnings.filterwarnings("ignore", category=ignore_warning)

            def __exit__(self, exception_type, exception_value, traceback):
                if not exception_value:
                    return

                try:
                    raise exception_value from exception_value
                except request_error as ex:
                    detail = ex.info["error"]
                    detail = detail.get("root_cause", [])[0].get("reason")
                    if ex.error == "search_phase_execution_exception":
                        detail = detail or ex.info["error"]
                        raise InvalidTextSearchError(detail)
                    elif ex.error == "index_closed_exception":
                        raise ClosedIndexError(index)
                    raise InvalidSearchError(ex) from exception_value
                except bulk_error as ex:
                    errors = [
                        WrongLogDataError.Error(
                            reason=action_error.get("error").get("reason"),
                            caused_by=action_error.get("error").get("caused_by"),
                        )
                        for error in ex.errors
                        for action_error in error.values()
                        if action_error.get("error")
                    ]
                    raise WrongLogDataError(errors=errors)
                except not_found_error as ex:
                    raise IndexNotFoundError(ex)
                except generic_api_error as ex:
                    raise GenericSearchError(ex)

        return _InnerContext()
