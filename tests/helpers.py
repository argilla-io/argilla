from typing import List

from fastapi import FastAPI
from starlette.testclient import TestClient

from rubrix._constants import API_KEY_HEADER_NAME, RUBRIX_WORKSPACE_HEADER_NAME
from rubrix.client.api import active_api
from rubrix.server.security import auth
from rubrix.server.security.auth_provider.local.settings import settings
from rubrix.server.security.auth_provider.local.users.model import UserInDB


class SecuredClient:
    def __init__(self, client: TestClient):
        self._client = client
        self._header = {API_KEY_HEADER_NAME: settings.default_apikey}
        self._current_user = None

    @property
    def fastpi_app(self) -> FastAPI:
        return self._client.app

    def change_current_user(self, username):
        default_user = auth.users.__dao__.__users__["rubrix"]
        new_user = UserInDB(
            username=username,
            hashed_password=username,  # Even if required, we can ignore it
            api_key=username,
            workspaces=["rubrix"],  # The default workspace
        )

        auth.users.__dao__.__users__[username] = new_user
        rb_api = active_api()
        rb_api._user = new_user
        rb_api.set_workspace(default_user.username)
        rb_api.client.token = new_user.api_key
        self._header[API_KEY_HEADER_NAME] = new_user.api_key
        self._header[RUBRIX_WORKSPACE_HEADER_NAME] = "rubrix"

    def reset_default_user(self):
        default_user = auth.users.__dao__.__users__["rubrix"]

        rb_api = active_api()
        rb_api._user = default_user
        rb_api.client.token = default_user.api_key
        rb_api.client.headers.pop(RUBRIX_WORKSPACE_HEADER_NAME)
        self._header[API_KEY_HEADER_NAME] = default_user.api_key

    def add_workspaces_to_rubrix_user(self, workspaces: List[str]):
        rubrix_user = auth.users.__dao__.__users__["rubrix"]
        rubrix_user.workspaces.extend(workspaces or [])

        rb_api = active_api()
        rb_api._user = rubrix_user

    def reset_rubrix_workspaces(self):
        rubrix_user = auth.users.__dao__.__users__["rubrix"]
        rubrix_user.workspaces = ["", "rubrix"]

        rb_api = active_api()
        rb_api._user = rubrix_user
        rb_api.set_workspace("rubrix")

    def delete(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}
        return self._client.delete(*args, headers=headers, **kwargs)

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
        method = kwargs.pop("method", None)
        if method is None:
            args = list(args)
            method = args.pop(0)
        if method == "POST":
            return self._client.post(*args, headers=headers, stream=True, **kwargs)
        if method == "GET":
            return self._client.get(*args, headers=headers, stream=True, **kwargs)
        raise NotImplementedError
