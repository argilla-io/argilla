from fastapi.testclient import TestClient

from temporal.app import app

client = TestClient(app)


def test_auth0():

    response = client.get("/access")