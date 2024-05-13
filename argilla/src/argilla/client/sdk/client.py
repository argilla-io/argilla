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
import datetime
import functools
import inspect
import json
import uuid
from json import JSONEncoder
from typing import Any, Dict, Optional, TypeVar
from urllib.parse import urlparse

import httpx

from argilla._constants import API_KEY_HEADER_NAME
from argilla.client.sdk._helpers import build_raw_response
from argilla.client.sdk.commons.errors import BaseClientError


@dataclasses.dataclass
class _ClientCommonDefaults:
    __httpx__: httpx.Client = dataclasses.field(default=None, init=False, compare=False)

    cookies: Dict[str, str] = dataclasses.field(default_factory=dict)
    headers: Dict[str, str] = dataclasses.field(default_factory=dict)
    timeout: float = 5.0
    httpx_extra_kwargs: Optional[Dict[str, Any]] = None

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in all endpoints"""
        return {**self.headers}

    def get_cookies(self) -> Dict[str, str]:
        return {**self.cookies}

    def get_timeout(self) -> float:
        return self.timeout

    def update_headers(self, headers: Dict[str, str]):
        self.headers.update(headers)
        self.httpx.headers.update(self.get_headers())

    @property
    def httpx(self):
        return self.__httpx__


@dataclasses.dataclass
class _Client:
    base_url: str

    def __post_init__(self):
        self.base_url = self.base_url.strip()
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        url = urlparse(self.base_url)
        if url.scheme == "https" and "_" in url.hostname:
            self.__httpx__ = None
            raise ValueError(
                'Avoid using hostnames with underscores "_". For reference see:'
                " https://stackoverflow.com/questions/10959757/the-use-of-the-underscore-in-host-names"
            )


@dataclasses.dataclass
class _AuthenticatedClient(_Client):
    token: str


class _EnhancedJSONEncoder(JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return super().default(o)


@dataclasses.dataclass
class Client(_ClientCommonDefaults, _Client):
    def __post_init__(self):
        super().__post_init__()
        self.httpx_extra_kwargs = self.httpx_extra_kwargs or {}
        self.__httpx__ = httpx.Client(
            base_url=self.base_url,
            headers=self.get_headers(),
            cookies=self.get_cookies(),
            timeout=self.get_timeout(),
            **self.httpx_extra_kwargs,
        )
        # TODO: Remove this NOW!!!!
        self.__http_async__ = httpx.AsyncClient(
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
                err_str = f"Your Api endpoint at {self.base_url} is not available or not responding: {err}"
                raise BaseClientError(err_str) from err

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
    def patch(self, path: str, *args, **kwargs):
        path = self._normalize_path(path)

        response = self.__httpx__.patch(
            url=path,
            headers=self.get_headers(),
            *args,
            **kwargs,
        )
        return build_raw_response(response).parsed

    @with_httpx_error_handler
    def patch(
        self,
        path: str,
        *args,
        json: Optional[dict] = None,
        **kwargs,
    ):
        path = self._normalize_path(path)
        body = self._normalize_body(json)
        response = self.__httpx__.patch(
            url=path,
            headers=self.get_headers(),
            json=body,
            *args,
            **kwargs,
        )
        return build_raw_response(response).parsed

    @with_httpx_error_handler
    def post(
        self,
        path: str,
        *args,
        json: Optional[dict] = None,
        **kwargs,
    ):
        path = self._normalize_path(path)
        body = self._normalize_body(json)
        response = self.__httpx__.post(
            url=path,
            headers=self.get_headers(),
            json=body,
            *args,
            **kwargs,
        )
        return build_raw_response(response).parsed

    @with_httpx_error_handler
    def put(
        self,
        path: str,
        *args,
        json: Optional[dict] = None,
        **kwargs,
    ):
        path = self._normalize_path(path)
        body = self._normalize_body(json)
        response = self.__httpx__.put(
            url=path,
            headers=self.get_headers(),
            json=body,
            *args,
            **kwargs,
        )
        return build_raw_response(response).parsed

    @with_httpx_error_handler
    def delete(
        self,
        path: str,
        *args,
        json: Optional[dict] = None,
        **kwargs,
    ):
        path = self._normalize_path(path)
        body = self._normalize_body(json)
        response = self.__httpx__.request(
            method="DELETE",
            url=path,
            headers=self.get_headers(),
            json=body,
            *args,
            **kwargs,
        )
        return build_raw_response(response).parsed

    @staticmethod
    def _normalize_path(path: str) -> str:
        path = path.strip()
        if path.startswith("/"):
            return path[1:]
        return path

    @classmethod
    def _normalize_body(cls, body: dict) -> dict:
        json_str = json.dumps(
            body,
            cls=_EnhancedJSONEncoder,
        )
        return json.loads(json_str)


ResponseType = TypeVar("ResponseType")


@dataclasses.dataclass
class AuthenticatedClient(Client, _ClientCommonDefaults, _AuthenticatedClient):
    """A Client which has been authenticated for use on secured endpoints"""

    def __hash__(self):
        return hash((self.base_url, self.token))

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in authenticated endpoints"""
        return {
            API_KEY_HEADER_NAME: self.token,
            **super().get_headers(),
        }
