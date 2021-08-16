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
