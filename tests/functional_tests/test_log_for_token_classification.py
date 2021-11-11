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


def test_log_record_that_makes_me_cry(monkeypatch):
    mocking_client(monkeypatch, client)
    dataset = "test_log_record_that_makes_me_cry"
    record = TokenClassificationRecord(
        text="'Secret Story : Última hora' debuta con un pobre 8.7% en el access de Telecinco.. . PROGRAMAS CON MEJOR CUOTA DEL LUNES (POR CADENAS). . ",
        tokens=[
            "'",
            "Secret",
            "Story",
            ":",
            "Última",
            "hora",
            "'",
            "debuta",
            "con",
            "un",
            "pobre",
            "8.7%",
            "en",
            "el",
            "access",
            "de",
            "Telecinco",
            "..",
            ".",
            "PROGRAMAS",
            "CON",
            "MEJOR",
            "CUOTA",
            "DEL",
            "LUNES",
            "(",
            "POR",
            "CADENAS",
            ")",
            ".",
            ".",
        ],
        prediction=[("ENG", 60, 66)],
        annotation=None,
        prediction_agent=None,
        annotation_agent=None,
        id=None,
        metadata={"section": "television", "newspaper": "eldiario"},
        status="Default",
        event_timestamp=None,
    )
    rubrix.delete(dataset)
    rubrix.log(record, name=dataset)

    records = rubrix.load(dataset,as_pandas=False)
    assert len(records) == 1
    assert records[0].text == record.text
    assert records[0].tokens == record.tokens
