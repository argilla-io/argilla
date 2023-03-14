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
import random
from json import JSONDecodeError
from time import sleep
from typing import Any, Dict, Iterable, Mapping, Optional, Type, TypeVar, Union

import httpx

from argilla.client.sdk.commons.errors import WrongResponseError
from argilla.client.sdk.commons.errors_handler import handle_response_error
from argilla.client.sdk.commons.models import (
    ErrorMessage,
    HTTPValidationError,
    Response,
)


def build_raw_response(
    response: httpx.Response,
) -> Response[Union[Dict[str, Any], ErrorMessage, HTTPValidationError]]:
    return build_typed_response(response)


ResponseType = TypeVar("ResponseType")


def build_typed_response(
    response: httpx.Response,
    response_type_class: Optional[Type[ResponseType]] = None,
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


class RetryTransport(httpx.AsyncBaseTransport, httpx.BaseTransport):
    RETRYABLE_METHODS = frozenset(["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"])
    RETRYABLE_STATUS_CODES = frozenset([413, 429, 503, 504])

    MAX_BACKOFF_WAIT = 30

    def __init__(
        self,
        wrapped_transport: Union[httpx.BaseTransport, httpx.AsyncBaseTransport],
        max_attempts: int = 5,
        max_backoff_wait: float = MAX_BACKOFF_WAIT,
        backoff_factor: float = 0.1,
        jitter_ratio: float = 0.1,
        respect_retry_after_header: bool = True,
        retryable_methods: Iterable[str] = None,
        retry_status_codes: Iterable[int] = None,
    ) -> None:
        self.wrapped_transport = wrapped_transport
        if jitter_ratio < 0 or jitter_ratio > 0.5:
            raise ValueError(f"jitter ratio should be between 0 and 0.5, actual {jitter_ratio}")

        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
        self.respect_retry_after_header = respect_retry_after_header
        self.retryable_methods = frozenset(retryable_methods) if retryable_methods else self.RETRYABLE_METHODS
        self.retry_status_codes = frozenset(retry_status_codes) if retry_status_codes else self.RETRYABLE_STATUS_CODES
        self.jitter_ratio = jitter_ratio
        self.max_backoff_wait = max_backoff_wait

    def _calculate_sleep(self, attempts_made: int, headers: Union[httpx.Headers, Mapping[str, str]]) -> float:
        retry_after_header = (headers.get("Retry-After") or "").strip()
        if self.respect_retry_after_header and retry_after_header:
            if retry_after_header.isdigit():
                return float(retry_after_header)

        backoff = self.backoff_factor * (2 ** (attempts_made - 1))
        jitter = (backoff * self.jitter_ratio) * random.choice([1, -1])
        total_backoff = backoff + jitter
        return min(total_backoff, self.max_backoff_wait)

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        response = self.wrapped_transport.handle_request(request)

        if request.method not in self.retryable_methods:
            return response

        remaining_attempts = self.max_attempts - 1
        attempts_made = 1

        while True:
            if remaining_attempts < 1 or response.status_code not in self.retry_status_codes:
                return response

            response.close()

            sleep_for = self._calculate_sleep(attempts_made, response.headers)
            sleep(sleep_for)

            response = self.wrapped_transport.handle_request(request)

            attempts_made += 1
            remaining_attempts -= 1

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        response = await self.wrapped_transport.handle_async_request(request)

        if request.method not in self.retryable_methods:
            return response

        remaining_attempts = self.max_attempts - 1
        attempts_made = 1

        while True:
            if remaining_attempts < 1 or response.status_code not in self.retry_status_codes:
                return response

            response.close()

            sleep_for = self._calculate_sleep(attempts_made, response.headers)
            sleep(sleep_for)

            response = await self.wrapped_transport.handle_async_request(request)

            attempts_made += 1
            remaining_attempts -= 1
