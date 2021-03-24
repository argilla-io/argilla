import pytest
from fastapi.testclient import TestClient
from rubrix import __version__ as rubrix_version
from rubrix.server.info.model import ApiInfo, ApiStatus
from rubrix.server.server import app

client = TestClient(app)


def test_api_info():

    response = client.get("/api/_info")
    assert response.status_code == 200

    info = ApiInfo.parse_obj(response.json())

    assert info.rubrix_version == rubrix_version


def test_api_status():

    response = client.get("/api/_status")

    assert response.status_code == 200

    info = ApiStatus.parse_obj(response.json())

    assert info.rubrix_version == rubrix_version

    # Checking to not get the error dictionary service.py includes whenever something goes wrong
    assert not "error" in info.elasticsearch

    # Checking that the first key into mem_info dictionary has a nont-none value
    assert "rss" in info.mem_info is not None
