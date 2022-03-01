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
import httpx
import pytest

import rubrix as rb
from rubrix.client import api
from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.errors import UnauthorizedApiError


@pytest.fixture
def mock_response_200(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 200 status code, emulating the correct login.
    """

    def mock_get(url, *args, **kwargs):
        if "/api/me" in url:
            return httpx.Response(status_code=200, json={"username": "booohh"})
        return httpx.Response(status_code=200)

    monkeypatch.setattr(httpx, "get", mock_get)


@pytest.fixture
def mock_response_500(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 500 status code, emulating an invalid state of the API error.
    """

    def mock_get(*args, **kwargs):
        return httpx.Response(status_code=500)

    monkeypatch.setattr(httpx, "get", mock_get)


@pytest.fixture
def mock_response_token_401(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 401 status code, emulating an invalid credentials error when using tokens to log in.
    Iterable structure to be able to pass the first 200 status code check
    """
    response_200 = httpx.Response(status_code=200)
    response_401 = httpx.Response(status_code=401)

    def mock_get(*args, **kwargs):
        if kwargs["url"] == "fake_url/api/me":
            return response_401
        elif kwargs["url"] == "fake_url/api/docs/spec.json":
            return response_200

    monkeypatch.setattr(httpx, "get", mock_get)


def test_init_correct(mock_response_200):
    """Testing correct default initalization

    It checks if the _client created is a RubrixClient object.
    """

    rb.init()
    assert api._CLIENT == AuthenticatedClient(
        base_url="http://localhost:6900", token="rubrix.apikey", timeout=60.0
    )
    assert api._USER == api.User(username="booohh")

    rb.init(api_url="mock_url", api_key="mock_key", workspace="mock_ws", timeout=42)
    assert api._CLIENT == AuthenticatedClient(
        base_url="mock_url",
        token="mock_key",
        timeout=42,
        headers={"X-Rubrix-Workspace": "mock_ws"},
    )


def test_init_incorrect(mock_response_500):
    """Testing incorrect default initalization

    It checks an Exception is raised with the correct message.
    """

    with pytest.raises(
        Exception,
        match="Connection error: Undetermined error connecting to the Rubrix Server. The API answered with a 500 code: b",
    ):
        rb.init()


def test_init_token_auth_fail(mock_response_token_401):
    """Testing initalization with failed authentication

    It checks an Exception is raised with the correct message.
    """
    with pytest.raises(UnauthorizedApiError):
        rb.init(api_url="fake_url", api_key="422")


def test_init_evironment_url(mock_response_200, monkeypatch):
    """Testing initalization with api_url provided via environment variable

    It checks the url in the environment variable gets passed to client.
    """
    monkeypatch.setenv("RUBRIX_API_URL", "mock_url")
    monkeypatch.setenv("RUBRIX_API_KEY", "mock_key")
    monkeypatch.setenv("RUBRIX_WORKSPACE", "mock_workspace")
    rb.init()

    assert api._CLIENT == AuthenticatedClient(
        base_url="mock_url",
        token="mock_key",
        timeout=60,
        headers={"X-Rubrix-Workspace": "mock_workspace"},
    )


def test_trailing_slash(mock_response_200):
    """Testing initalization with provided api_url via environment variable and argument

    It checks the trailing slash is removed in all cases
    """
    rb.init(api_url="http://mock.com/")
    assert api._CLIENT.base_url == "http://mock.com"
