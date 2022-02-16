from starlette.testclient import TestClient

from rubrix._constants import API_KEY_HEADER_NAME
from rubrix.server.security.auth_provider.local.settings import settings


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
