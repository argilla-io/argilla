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

from argilla_server.models import User
from argilla_v1._constants import (
    API_KEY_HEADER_NAME,
    WORKSPACE_HEADER_NAME,
)
from fastapi import FastAPI
from starlette.testclient import TestClient


class SecuredClient:
    def __init__(self, client: "TestClient", argilla_user: User):
        self._client = client
        self._header = {API_KEY_HEADER_NAME: argilla_user.api_key, WORKSPACE_HEADER_NAME: argilla_user.username}
        self._current_user = None

    def update_api_key(self, api_key):
        self._header[API_KEY_HEADER_NAME] = api_key

    @property
    def fastpi_app(self) -> FastAPI:
        return self._client.app

    def delete(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}

        return self._client.request("DELETE", *args, headers=headers, **kwargs)

    def request(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}
        return self._client.request(*args, headers=headers, **kwargs)

    def post(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}
        return self._client.post(*args, headers=headers, **kwargs)

    async def post_async(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def get(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}
        return self._client.get(*args, headers=headers, **kwargs)

    def put(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}
        return self._client.put(*args, headers=headers, **kwargs)

    def patch(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}
        return self._client.patch(*args, headers=headers, **kwargs)

    def stream(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}

        if hasattr(self._client, "stream"):
            return self._client.stream(
                *args,
                headers=headers,
                **kwargs,
            )
        else:  # Old fashion way
            method = kwargs.pop("method", None)
            if method is None:
                args = list(args)
                method = args.pop(0)
            if method == "POST":
                func = self._client.post
            elif method == "GET":
                func = self._client.get
            else:
                raise NotImplementedError()

            return func(
                *args,
                headers=headers,
                stream=True,
                **kwargs,
            )
