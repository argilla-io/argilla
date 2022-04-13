from typing import List

from fastapi import FastAPI
from starlette.testclient import TestClient

import rubrix
from rubrix._constants import API_KEY_HEADER_NAME
from rubrix.server.security import auth
from rubrix.server.security.auth_provider.local.settings import settings


class SecuredClient:
    def __init__(self, client: TestClient):
        self._client = client
        self._header = {API_KEY_HEADER_NAME: settings.default_apikey}

    @property
    def fastpi_app(self) -> FastAPI:
        return self._client.app

    def add_workspaces_to_rubrix_user(self, workspaces: List[str]):
        rubrix_user = auth.users.__dao__.__users__["rubrix"]
        workspaces = workspaces or []
        workspaces.extend(rubrix_user.workspaces or [])
        rubrix_user.workspaces = workspaces

        rubrix.init()

    def reset_rubrix_workspaces(self):
        rubrix_user = auth.users.__dao__.__users__["rubrix"]
        rubrix_user.workspaces = None

        rubrix.init()

    def delete(self, *args, **kwargs):
        request_headers = kwargs.pop("headers", {})
        headers = {**self._header, **request_headers}
        return self._client.delete(*args, headers=headers, **kwargs)

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
