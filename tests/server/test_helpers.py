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

from rubrix._constants import API_KEY_HEADER_NAME
from rubrix.server.security.auth_provider.local.settings import settings
from rubrix.server.server import app
from starlette.testclient import TestClient


class SecuredClient:
    def __init__(self, client: TestClient):
        self._client = client
        self._header = {API_KEY_HEADER_NAME: settings.default_apikey}

    def delete(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}
        return self._client.delete(*args, headers=headers, **kwargs)

    def post(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}
        return self._client.post(*args, headers=headers, **kwargs)

    def get(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}
        return self._client.get(*args, headers=headers, **kwargs)

    def put(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}
        return self._client.put(*args, headers=headers, **kwargs)


client = SecuredClient(TestClient(app))
