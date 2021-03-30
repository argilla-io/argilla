# -*- coding: utf-8 -*-

"""Rubrix Log Test Unit

This pytest modules aims to test the correct state to the log function.
Interaction with the client will be mocked, as this test are independent from the API,
which could or could not be mounted.
"""


import pytest
import requests
import rubrix
from rubrix import (
    BulkResponse,
    EntitySpan,
    TextClassificationRecord,
    TokenClassificationAnnotation,
    TokenClassificationRecord,
)
from rubrix.sdk.api.text_classification import bulk_records as text_classification_bulk
from rubrix.sdk.api.token_classification import (
    bulk_records as token_classification_bulk,
)
from rubrix.sdk.models import (
    TextClassificationBulkDataMetadata,
    TextClassificationBulkDataTags,
    TextClassificationRecordsBulk,
    TokenClassificationBulkDataMetadata,
    TokenClassificationBulkDataTags,
    TokenClassificationRecordsBulk,
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
        response = requests.models.Response()
        response.status_code = 200
        return response

    monkeypatch.setattr(
        requests, "get", mock_get
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

    def mock_get(*args, json_body: TextClassificationRecordsBulk, **kwargs):
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

    def mock_get(*args, json_body: TokenClassificationRecordsBulk, **kwargs):
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


@pytest.fixture
def mock_dataset_text():
    """Mocked dataset for text classification"""

    return [
        TextClassificationRecord(
            id="test",
            inputs={"review_body": "increible test"},
            metadata={"product_category": "test de pytest"},
        )
    ]


@pytest.fixture
def mock_dataset_token():
    """Mocked dataset for token classification"""

    return [
        TokenClassificationRecord(
            raw_text="Super test",
            prediction=TokenClassificationAnnotation(
                agent="spacy",
                entities=[
                    EntitySpan(start=0, end=5, start_token=0, end_token=3, label="e")
                ],
            ),
            tokens=["a", "b"],
            metadata={"model": "spacy_es_core_news_sm"},
        )
    ]


@pytest.fixture
def mock_tags_text():
    """Mocked tagst for text classification"""

    return {
        "type": "sentiment classifier",
        "lang": "spanish",
        "description": "Spanish sentiment classifier with `multifield inputs` (title and body)",
    }


@pytest.fixture
def mock_tags_token():
    """Mocked dataset for token classification"""

    return {
        "type": "sentiment classifier",
        "lang": "spanish",
        "description": "Spanish sentiment classifier with `multifield inputs` (title and body)",
    }


def test_text_classification(
    mock_response_200,
    mock_dataset_text,
    mock_tags_text,
    mock_response_text,
):
    """Testing text classification with log function

    It checks a Response is generated.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response, emulating API init
    mock_dataset_text
        Mocked ClassificationRecord list to log
    mock_tags_text
        Mocked tags dictionary for text classification
    mock_response_text
        Mocked response given by the sync method, emulating the log of data
    """

    assert rubrix.log(
        name="test", records=mock_dataset_text, tags=mock_tags_text
    ) == BulkResponse(dataset="test", processed= 500, failed=0)


def test_token_classification(
    mock_response_200, mock_dataset_token, mock_tags_token, mock_response_token
):
    """Testing token classification with log function

    It checks a Response is generated.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response, emulating API init
    mock_dataset_token
        Mocked ClassificationRecord list to log
    mock_tags_token
        Mocked tags dictionary for token classification
    mock_response_token
        Mocked response given by the sync method, emulating the log of data
    """

    assert rubrix.log(
        name="test", records=mock_dataset_token, tags=mock_tags_token
    ) == BulkResponse(dataset="test", processed= 500, failed=0)


def test_no_name(
    mock_response_200, mock_dataset_token, mock_tags_token, mock_response_token
):
    """Testing classification with no input name

    It checks an Exception is raised, with the corresponding message.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response, emulating API init
    mock_dataset_token
        Mocked ClassificationRecord list to log
    mock_tags_token
        Mocked tags dictionary for token classification
    mock_response_token
        Mocked response given by the sync method, emulating the log of data
    """

    with pytest.raises(
        Exception, match="Empty project name has been passed as argument."
    ):

        assert rubrix.log(
            name="", records=mock_dataset_token, tags=mock_tags_token
        ) == BulkResponse.from_dict({"dataset": "test", "processed": 500, "failed": 0})


def test_empty_records(mock_response_200, mock_response_token, mock_tags_token):
    """Testing classification with empty record list

    It checks an Exception is raised, with the corresponding message.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response, emulating API init
    mock_dataset_token
        Mocked ClassificationRecord list to log
    mock_tags_token
        Mocked tags dictionary for token classification
    mock_response_token
        Mocked response given by the sync method, emulating the log of data
    """

    with pytest.raises(
        Exception, match="Empty record list has been passed as argument."
    ):
        assert rubrix.log(
            name="test", records=[], tags=mock_tags_token
        ) == BulkResponse.from_dict({"dataset": "test", "processed": 500, "failed": 0})


def test_unknow_record_type(
    mock_response_200, mock_dataset_token, mock_response_token, mock_tags_token
):
    """Testing classification with unknown record type

    It checks an Exception is raised, with the corresponding message.

    Parameters
    ----------
    mock_response_200
        Mocked correct http response, emulating API init
    mock_dataset_token
        Mocked ClassificationRecord list to log
    mock_tags_token
        Mocked tags dictionary for token classification
    mock_response_token
        Mocked response given by the sync method, emulating the log of data
    """

    with pytest.raises(Exception, match="Unknown record type passed as argument."):
        assert rubrix.log(
            name="test", records=["12"], tags=mock_tags_token
        ) == BulkResponse.from_dict({"dataset": "test", "processed": 500, "failed": 0})


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
            records=[
                TextClassificationRecord(inputs={"text": "The textual info"})
            ],
            tags={"env": "Test"},
        )
