# -*- coding: utf-8 -*-

"""Rubrix Log Test Unit

This pytest modules aims to test the correct state to the log function.
Interaction with the client will be mocked, as this test are independent from the API,
which could or could not be mounted.
"""
from typing import cast

import httpx
import pytest
import rubrix
import logging

from rubrix import (
    BulkResponse,
    TextClassificationRecord,
    TokenClassificationRecord,
)
from rubrix.sdk.api.text_classification import bulk_records as text_classification_bulk
from rubrix.sdk.api.token_classification import (
    bulk_records as token_classification_bulk,
)
from rubrix.sdk.models import (
    TextClassificationBulkData,
    TextClassificationBulkDataMetadata,
    TextClassificationBulkDataTags,
    TokenClassificationBulkData,
    TokenClassificationBulkDataMetadata,
    TokenClassificationBulkDataTags,
)
from rubrix.sdk.types import Response


@pytest.fixture
def mock_response_200(monkeypatch):
    """Mock_get method from the class, and monkeypatch application.

    It will return a 200 status code in the init function, emulating the correct login.

    Parameters
    ----------
    monkeypatch
        Mockup function
    """

    def mock_get(*args, **kwargs):
        return httpx.Response(200)

    monkeypatch.setattr(
        httpx, "get", mock_get
    )  # apply the monkeypatch for requests.get to mock_get


@pytest.fixture
def mock_response_text(monkeypatch):
    """Mock_get method from the class, and monkeypatch application.

    It will text classification response from the API.

    Parameters
    ----------
    monkeypatch
        Mockup function
    """

    _response = BulkResponse(dataset="test", processed=500, failed=0)

    def mock_get(*args, json_body: TextClassificationBulkData, **kwargs):
        assert isinstance(json_body.metadata, TextClassificationBulkDataMetadata)
        assert isinstance(json_body.tags, TextClassificationBulkDataTags)
        return Response(
            status_code=200,
            content=b"Everything's fine",
            headers={
                "date": "Tue, 09 Mar 2021 10:18:23 GMT",
                "server": "uvicorn",
                "content-length": "43",
                "content-type": "application/json",
            },
            parsed=_response,
        )

    monkeypatch.setattr(
        text_classification_bulk, "sync_detailed", mock_get
    )  # apply the monkeypatch for requests.get to mock_get


@pytest.fixture
def mock_response_token(monkeypatch):
    """Mock_get method from the class, and monkeypatch application.

    It will token classification response from the API.

    Parameters
    ----------
    monkeypatch
        Mockup function
    """

    _response = BulkResponse(dataset="test", processed=500, failed=0)

    def mock_get(*args, json_body: TokenClassificationBulkData, **kwargs):
        assert isinstance(json_body.metadata, TokenClassificationBulkDataMetadata)
        assert isinstance(json_body.tags, TokenClassificationBulkDataTags)
        return Response(
            status_code=200,
            content=b"Everything's fine",
            headers={
                "date": "Tue, 09 Mar 2021 10:18:23 GMT",
                "server": "uvicorn",
                "content-length": "43",
                "content-type": "application/json",
            },
            parsed=_response,
        )

    monkeypatch.setattr(
        token_classification_bulk, "sync_detailed", mock_get
    )  # apply the monkeypatch for requests.get to mock_get


def test_text_classification(mock_response_200, mock_response_text):
    """Testing text classification with log function

    It checks a Response is generated.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response, emulating API init
    mock_response_text
        Mocked response given by the sync method, emulating the log of data
    """
    records = [
        TextClassificationRecord(
            inputs={"review_body": "increible test"},
            prediction=[("test", 0.9), ("test2", 0.1)],
            annotation="test",
            metadata={"product_category": "test de pytest"},
            id="test",
        )
    ]

    assert (
        rubrix.log(
            name="test",
            records=records,
            tags={"type": "sentiment classifier", "lang": "spanish"},
        )
        == BulkResponse(dataset="test", processed=500, failed=0)
    )


def test_token_classification(mock_response_200, mock_response_token):
    """Testing token classification with log function

    It checks a Response is generated.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response, emulating API init
    mock_response_token
        Mocked response given by the sync method, emulating the log of data
    """
    records = [
        TokenClassificationRecord(
            text="Super test",
            tokens=["Super", "test"],
            prediction=[("test", 6, 10)],
            annotation=[("test", 6, 10)],
            prediction_agent="spacy",
            annotation_agent="recognai",
            metadata={"model": "spacy_es_core_news_sm"},
            id=1,
        )
    ]

    assert (
        rubrix.log(
            name="test",
            records=records[0],
            tags={"type": "sentiment classifier", "lang": "spanish"},
        )
        == BulkResponse(dataset="test", processed=500, failed=0)
    )


def test_no_name(mock_response_200):
    """Testing classification with no input name

    It checks an Exception is raised, with the corresponding message.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response, emulating API init
    """

    with pytest.raises(
        Exception, match="Empty project name has been passed as argument."
    ):
        assert rubrix.log(name="", records=cast(TextClassificationRecord, None))


def test_empty_records(mock_response_200):
    """Testing classification with empty record list

    It checks an Exception is raised, with the corresponding message.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response, emulating API init
    """

    with pytest.raises(
        Exception, match="Empty record list has been passed as argument."
    ):
        rubrix.log(name="test", records=[])


def test_unknow_record_type(mock_response_200):
    """Testing classification with unknown record type

    It checks an Exception is raised, with the corresponding message.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response, emulating API init
    """

    with pytest.raises(Exception, match="Unknown record type passed as argument."):
        rubrix.log(name="test", records=["12"])


@pytest.fixture
def mock_wrong_bulk_response(monkeypatch):
    def mock(*args, **kwargs):
        return Response(
            status_code=500,
            headers={},
            content=b"",
            parsed={"error": "the error message "},
        )

    monkeypatch.setattr(text_classification_bulk, "sync_detailed", mock)


def test_wrong_response(mock_response_200, mock_wrong_bulk_response):
    rubrix._client = None
    with pytest.raises(
        Exception,
        match="Connection error: API is not responding. The API answered with",
    ):
        rubrix.log(
            name="dataset",
            records=[TextClassificationRecord(inputs={"text": "The textual info"})],
            tags={"env": "Test"},
        )


def test_info_message(mock_response_200, mock_response_text, caplog):
    """Testing initialization info message

    Parameters
    ----------
    mock_response_200
        Mocked correct http response, emulating API init
    mock_response_text
        Mocked response given by the sync method, emulating the log of data
    caplog
        Captures the logging output
    """

    rubrix._client = None  # Force client initialization
    caplog.set_level(logging.INFO)

    records = [
        TextClassificationRecord(
            inputs={"review_body": "increible test"},
            prediction=[("test", 0.9), ("test2", 0.1)],
            annotation="test",
            metadata={"product_category": "test de pytest"},
            id="test",
        )
    ]

    rubrix.log(
        name="test",
        records=records,
        tags={"type": "sentiment classifier", "lang": "spanish"},
    )

    print(caplog.text)

    assert "Rubrix has been initialized on http://localhost:6900" in caplog.text
