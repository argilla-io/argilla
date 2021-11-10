import pytest

import rubrix
from rubrix import TokenClassificationRecord
from tests.server.test_helpers import client, mocking_client


def test_log_with_empty_text(monkeypatch):
    mocking_client(monkeypatch, client)
    dataset = "test_log_with_empty_text"
    text = " "

    rubrix.delete(dataset)
    with pytest.raises(Exception, match="No text or empty text provided"):
        rubrix.log(
            TokenClassificationRecord(id=0, text=text, tokens=["a", "b", "c"]),
            name=dataset,
        )


def test_log_with_empty_tokens_list(monkeypatch):
    mocking_client(monkeypatch, client)
    dataset = "test_log_with_empty_text"
    text = "The text"

    rubrix.delete(dataset)
    with pytest.raises(
        Exception,
        match="ensure this value has at least 1 items",
    ):
        rubrix.log(
            TokenClassificationRecord(id=0, text=text, tokens=[]),
            name=dataset,
        )
