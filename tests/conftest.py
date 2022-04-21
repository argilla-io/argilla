import httpx
import pytest
from _pytest.logging import LogCaptureFixture
from loguru import logger
from starlette.testclient import TestClient

from rubrix import app
from tests.helpers import SecuredClient


@pytest.fixture
def mocked_client(monkeypatch):
    with TestClient(app, raise_server_exceptions=False) as _client:
        client = SecuredClient(_client)

        monkeypatch.setattr(httpx, "post", client.post)
        monkeypatch.setattr(httpx.AsyncClient, "post", client.post_async)
        monkeypatch.setattr(httpx, "get", client.get)
        monkeypatch.setattr(httpx, "delete", client.delete)
        monkeypatch.setattr(httpx, "put", client.put)
        monkeypatch.setattr(httpx, "stream", client.stream)

        yield client


@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)
