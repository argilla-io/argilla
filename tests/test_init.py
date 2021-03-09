# -*- coding: utf-8 -*-

"""Rubric Client Init Testing File"""

import pytest
import requests

import rubric
from rubric.client import RubricClient


@pytest.fixture
def mock_response_200(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 200 status code, emulating the correct login.

    Parameters
    ----------
    monkeypatch
        Mockup function
    """

    def mock_get(*args, **kwargs):
        response = requests.models.Response()
        response.status_code = 200
        return response

    monkeypatch.setattr(
        requests, "get", mock_get
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
        response = requests.models.Response()
        response.status_code = 500
        return response

    monkeypatch.setattr(
        requests, "get", mock_get
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
    response_200 = requests.models.Response()
    response_200.status_code = 200

    response_401 = requests.models.Response()
    response_401.status_code = 401

    def mock_get(*args, **kwargs):
        if kwargs["url"] == "fake_url/api/me":
            return response_401
        elif kwargs["url"] == "fake_url/openapi.json":
            return response_200

    monkeypatch.setattr(
        requests, "get", mock_get
    )  # apply the monkeypatch for requests.get to mock_get


def test_init_correct(mock_response_200):
    """Testing correct default initalization

    It checks if the _client created is a RubricClient object.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response
    """

    rubric.init()

    assert isinstance(rubric._client, RubricClient)


def test_init_incorrect(mock_response_500):
    """Testing incorrect default initalization

    It checks an Exception is raised with the correct message.

    Parameters
    ----------
    mock_response_500
        Mocked incorrect http response
    """

    rubric._client = None # assert empty client
    with pytest.raises(Exception, match="Unidentified error, it should not get here."):
        rubric.init()


def test_init_token_correct(mock_response_200):
    """Testing correct token initalization

    It checks if the _client created is a RubricClient object.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response
    """
    rubric._client = None  # assert empty client
    rubric.init(token="fjkjdf333")

    assert isinstance(rubric._client, RubricClient)


def test_init_token_incorrect(mock_response_500):
    """Testing incorrect token initalization

    It checks an Exception is raised with the correct message.

    Parameters
    ----------
    mock_response_500
        Mocked correct http response
    """
    rubric._client = None  # assert empty client
    with pytest.raises(Exception, match="Unidentified error, it should not get here."):
        rubric.init(token="422")


def test_init_token_auth_fail(mock_response_token_401):
    """Testing initalization with failed authentication

    It checks an Exception is raised with the correct message.

    Parameters
    ----------
    mock_response_401
        Mocked correct http response
    """
    rubric._client = None  # assert empty client
    with pytest.raises(Exception, match="Authentification error: invalid credentials."):
        rubric.init(api_url="fake_url", token="422")
