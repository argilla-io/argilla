# -*- coding: utf-8 -*-

"""Rubrix Client Init Testing File"""

import os

import httpx
import pytest
import rubrix
from rubrix.client import AuthenticatedClient, Client, RubrixClient


@pytest.fixture
def mock_response_200(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 200 status code, emulating the correct login.

    Parameters
    ----------
    monkeypatch
        Mockup function
    """

    def mock_get(url,*args, **kwargs):
        if "/api/me" in url:
            return httpx.Response(status_code=200,json={"username": "booohh"})
        return httpx.Response(status_code=200)

    monkeypatch.setattr(
        httpx, "get", mock_get
    )  # apply the monkeypatch for requests.get to mock_get


@pytest.fixture
def mock_response_500(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 500 status code, emulating an invalid state of the API error.

    Parameters
    ----------
    monkeypatch
        Mockup function

    """

    def mock_get(*args, **kwargs):
        return httpx.Response(status_code=500)

    monkeypatch.setattr(
        httpx, "get", mock_get
    )  # apply the monkeypatch for requests.get to mock_get


@pytest.fixture
def mock_response_token_401(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 401 status code, emulating an invalid credentials error when using tokens to log in.
    Iterable stucture to be able to pass the first 200 status code check

    Parameters
    ----------
    monkeypatch
        Mockup function

    """
    response_200 = httpx.Response(status_code=200)
    response_401 = httpx.Response(status_code=401)

    def mock_get(*args, **kwargs):
        if kwargs["url"] == "fake_url/api/me":
            return response_401
        elif kwargs["url"] == "fake_url/api/docs/spec.json":
            return response_200

    monkeypatch.setattr(
        httpx, "get", mock_get
    )  # apply the monkeypatch for requests.get to mock_get


@pytest.fixture
def api_url_env_var():
    """Sets an api_url via environment variable"""

    os.environ["RUBRIX_API_URL"] = "http://fakeurl.com"


@pytest.fixture
def api_url_env_var_trailing_slash():
    """Sets an api_url via environment variable. The url has trailing slash"""

    os.environ["RUBRIX_API_URL"] = "http://fakeurl.com/"


@pytest.fixture
def token_env_var():
    """Sets an api_url via environment variable"""

    os.environ["RUBRIX_API_KEY"] = "622"


def test_init_correct(mock_response_200):
    """Testing correct default initalization

    It checks if the _client created is a RubrixClient object.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response
    """

    rubrix.init()

    assert isinstance(rubrix._client, RubrixClient)


def test_init_incorrect(mock_response_500):
    """Testing incorrect default initalization

    It checks an Exception is raised with the correct message.

    Parameters
    ----------
    mock_response_500
        Mocked incorrect http response
    """

    rubrix._client = None  # assert empty client
    with pytest.raises(Exception, match="Unidentified error, it should not get here."):
        rubrix.init()


def test_init_token_correct(mock_response_200):
    """Testing correct token initalization

    It checks if the _client created is a RubrixClient object.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response
    """
    rubrix._client = None  # assert empty client
    rubrix.init(api_key="fjkjdf333")

    assert isinstance(rubrix._client, RubrixClient)


def test_init_token_incorrect(mock_response_500):
    """Testing incorrect token initalization

    It checks an Exception is raised with the correct message.

    Parameters
    ----------
    mock_response_500
        Mocked correct http response
    """
    rubrix._client = None  # assert empty client
    with pytest.raises(Exception, match="Unidentified error, it should not get here."):
        rubrix.init(api_key="422")


def test_init_token_auth_fail(mock_response_token_401):
    """Testing initalization with failed authentication

    It checks an Exception is raised with the correct message.

    Parameters
    ----------
    mock_response_401
        Mocked correct http response
    """
    rubrix._client = None  # assert empty client
    with pytest.raises(Exception, match="Authentification error: invalid credentials."):
        rubrix.init(api_url="fake_url", api_key="422")


def test_init_evironment_url(api_url_env_var, mock_response_200):
    """Testing initalization with api_url provided via environment variable

    It checks the url in the environment variable gets passed to client.

    Parameters
    ----------
    api_url_env_var
        Fixture to set the fake url in the env variable
    mock_response_200
        Mocked correct http response
    """
    rubrix._client = None  # assert empty client

    rubrix.init()

    assert isinstance(rubrix._client, RubrixClient)
    assert isinstance(rubrix._client._client, Client)
    assert rubrix._client._client.base_url == "http://fakeurl.com"


def test_init_evironment_url_token(api_url_env_var, token_env_var, mock_response_200):
    """Testing initalization with api_url and tokenprovided via environment variable

    It checks the url and token in the environment variable gets passed to client.

    Parameters
    ----------
    api_url_env_var
        Fixture to set the fake url in the env variable
    token_env_var
        Fixture to set the fake token in the env variable
    mock_response_200
        Mocked correct http response
    """
    rubrix._client = None  # assert empty client

    rubrix.init()

    assert isinstance(rubrix._client, RubrixClient)
    assert isinstance(rubrix._client._client, AuthenticatedClient)
    assert rubrix._client._client.base_url == "http://fakeurl.com"
    assert rubrix._client._client.token == str(622)


def test_init_evironment_no_url_token(token_env_var, mock_response_200):
    """Testing initalization with token provided via environment variable and api_url via args

    It checks a non-secured Client is created

    Parameters
    ----------
    token_env_var
        Fixture to set the fake token in the env variable
    mock_response_200
        Mocked correct http response
    """
    rubrix._client = None  # assert empty client

    rubrix.init(api_url="http://anotherfakeurl.com")

    assert isinstance(rubrix._client, RubrixClient)
    assert isinstance(rubrix._client._client, Client)
    assert rubrix._client._client.base_url == "http://anotherfakeurl.com"


def test_trailing_slash(api_url_env_var_trailing_slash, mock_response_200):
    """Testing initalization with provided api_url via environment variable and argument

    It checks the trailing slash is removed in all cases

    Parameters
    ----------
    api_url_env_var
        Fixture to set the fake url in the env variable, with trailing slash
    mock_response_200
        Mocked correct http response
    """

    rubrix._client = None  # assert empty client

    # Environment variable case
    rubrix.init(api_url="http://anotherfakeurl.com/")
    assert rubrix._client._client.base_url == "http://anotherfakeurl.com"

    rubrix._client = None  # assert empty client

    # Argument case
    rubrix.init()
    assert rubrix._client._client.base_url == "http://fakeurl.com"


def test_default_init(mock_response_200):
    rubrix._client = None

    if "RUBRIX_API_URL" in os.environ:
        del os.environ["RUBRIX_API_URL"]

    if "RUBRIX_API_KEY" in os.environ:
        del os.environ["RUBRIX_API_KEY"]

    rubrix.init()

    assert isinstance(rubrix._client._client, Client)
    assert rubrix._client._client.base_url == "http://localhost:6900"

    expected_token = "blablabla"
    rubrix.init(api_key=expected_token)
    assert isinstance(rubrix._client._client, AuthenticatedClient)
    assert rubrix._client._client.token == expected_token
