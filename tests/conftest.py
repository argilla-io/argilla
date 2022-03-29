import httpx
import pytest
from _pytest.logging import LogCaptureFixture
from loguru import logger
from starlette.testclient import TestClient

from rubrix import app
from tests.helpers import SecuredClient


@pytest.fixture
def mocked_client(monkeypatch):
    client = SecuredClient(TestClient(app, raise_server_exceptions=False))

    monkeypatch.setattr(httpx, "post", client.post)
    monkeypatch.setattr(httpx, "get", client.get)
    monkeypatch.setattr(httpx, "delete", client.delete)
    monkeypatch.setattr(httpx, "put", client.put)
    monkeypatch.setattr(httpx, "stream", client.stream)

    return client


@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)
