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

from typing import List

from argilla._constants import API_KEY_HEADER_NAME, WORKSPACE_HEADER_NAME
from argilla.client.api import active_api
from argilla.server.security import auth
from argilla.server.security.auth_provider.local.settings import settings
from argilla.server.security.auth_provider.local.users.model import UserInDB
from fastapi import FastAPI
from starlette.testclient import TestClient


class SecuredClient:
    def __init__(self, client: TestClient):
        self._client = client
        self._header = {
            API_KEY_HEADER_NAME: settings.default_apikey,
            WORKSPACE_HEADER_NAME: "argilla",  # Hard-coded default workspace
        }
        self._current_user = None

    @property
    def fastpi_app(self) -> FastAPI:
        return self._client.app

    def change_current_user(self, username):
        default_user = auth.users.__dao__.__users__["argilla"]
        new_user = UserInDB(
            username=username,
            hashed_password=username,  # Even if required, we can ignore it
            api_key=username,
            workspaces=["argilla"],  # The default workspace
        )

        auth.users.__dao__.__users__[username] = new_user
        rb_api = active_api()
        rb_api._user = new_user
        rb_api.set_workspace(default_user.username)
        rb_api.http_client.token = new_user.api_key
        self._header[API_KEY_HEADER_NAME] = new_user.api_key
        self._header[WORKSPACE_HEADER_NAME] = "argilla"

    def reset_default_user(self):
        default_user = auth.users.__dao__.__users__["argilla"]

        rb_api = active_api()
        rb_api._user = default_user
        rb_api.http_client.token = default_user.api_key
        rb_api.http_client.headers.pop(WORKSPACE_HEADER_NAME, None)
        self._header[API_KEY_HEADER_NAME] = default_user.api_key

    def add_workspaces_to_argilla_user(self, workspaces: List[str]):
        argilla_user = auth.users.__dao__.__users__["argilla"]
        argilla_user.workspaces.extend(workspaces or [])

        rb_api = active_api()
        rb_api._user = argilla_user

    def reset_argilla_workspaces(self):
        argilla_user = auth.users.__dao__.__users__["argilla"]
        argilla_user.workspaces = ["", "argilla"]

        rb_api = active_api()
        rb_api._user = argilla_user
        rb_api.set_workspace("argilla")

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
