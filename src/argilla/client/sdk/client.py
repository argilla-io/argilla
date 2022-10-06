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
import dataclasses
import functools
from typing import Dict, TypeVar

import httpx

from argilla._constants import _OLD_API_KEY_HEADER_NAME, API_KEY_HEADER_NAME
from argilla.client.sdk._helpers import build_raw_response
from argilla.client.sdk.commons.errors import BaseClientError


@dataclasses.dataclass
class _ClientCommonDefaults:
    __httpx__: httpx.Client = dataclasses.field(default=None, init=False, compare=False)

    cookies: Dict[str, str] = dataclasses.field(default_factory=dict)
    headers: Dict[str, str] = dataclasses.field(default_factory=dict)
    timeout: float = 5.0

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in all endpoints"""
        return {**self.headers}

    def get_cookies(self) -> Dict[str, str]:
        return {**self.cookies}

    def get_timeout(self) -> float:
        return self.timeout


@dataclasses.dataclass
class _Client:
    base_url: str

    def __post_init__(self):
        self.base_url = self.base_url.strip()
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]


@dataclasses.dataclass
class _AuthenticatedClient(_Client):
    token: str


@dataclasses.dataclass
class Client(_ClientCommonDefaults, _Client):
    def __post_init__(self):
        super().__post_init__()
        self.__httpx__ = httpx.Client(
            base_url=self.base_url,
            headers=self.get_headers(),
            cookies=self.get_cookies(),
            timeout=self.get_timeout(),
        )

    def __del__(self):
        del self.__httpx__

    def __hash__(self):
        return hash(self.base_url)

    def with_httpx_error_handler(func):
        @functools.wraps(func)
        def inner(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                return result
            except httpx.ConnectError as err:
                err_str = f"Your Api endpoint at {self.base_url} is not available or not responding."
                raise BaseClientError(err_str) from None

        return inner

    @with_httpx_error_handler
    def get(self, path: str, *args, **kwargs):
        path = self._normalize_path(path)
        response = self.__httpx__.get(
            url=path,
            headers=self.get_headers(),
            *args,
            **kwargs,
        )
        return build_raw_response(response).parsed

    @with_httpx_error_handler
    def post(self, path: str, *args, **kwargs):
        path = self._normalize_path(path)

        response = self.__httpx__.post(
            url=path,
            headers=self.get_headers(),
            *args,
            **kwargs,
        )
        return build_raw_response(response).parsed

    @with_httpx_error_handler
    def put(self, path: str, *args, **kwargs):
        path = self._normalize_path(path)
        response = self.__httpx__.put(
            url=path,
            headers=self.get_headers(),
            *args,
            **kwargs,
        )
        return build_raw_response(response).parsed

    @with_httpx_error_handler
    def delete(self, path: str, *args, **kwargs):
        path = self._normalize_path(path)
        response = self.__httpx__.request(
            method="DELETE",
            url=path,
            headers=self.get_headers(),
            *args,
            **kwargs,
        )
        return build_raw_response(response).parsed

    @with_httpx_error_handler
    def stream(self, path: str, *args, **kwargs):
        return self.__httpx__.stream(
            url=path,
            headers=self.get_headers(),
            timeout=None,  # Avoid timeouts. TODO: Improve the logic
            *args,
            **kwargs,
        )

    @staticmethod
    def _normalize_path(path: str) -> str:
        path = path.strip()
        if path.startswith("/"):
            return path[1:]
        return path


ResponseType = TypeVar("ResponseType")


@dataclasses.dataclass
class AuthenticatedClient(Client, _ClientCommonDefaults, _AuthenticatedClient):
    """A Client which has been authenticated for use on secured endpoints"""

    def __hash__(self):
        return hash((self.base_url, self.token))

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in authenticated endpoints"""
        return {
            "Authorization": f"Bearer {self.token}",  # Backward compatibility
            API_KEY_HEADER_NAME: self.token,
            _OLD_API_KEY_HEADER_NAME: self.token,
            **super().get_headers(),
        }
