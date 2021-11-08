import rubrix
from rubrix import TextClassificationRecord, TokenClassificationRecord
from tests.server.test_helpers import client, mocking_client


def test_delete_and_create_for_different_task(monkeypatch):
    mocking_client(monkeypatch, client)
    dataset = "test_delete_and_create_for_different_task"
    text = "This is a text"

    rubrix.delete(dataset)
    rubrix.log(TextClassificationRecord(id=0, inputs=text), name=dataset)
    rubrix.load(dataset)

    rubrix.delete(dataset)
    rubrix.log(
        TokenClassificationRecord(id=0, text=text, tokens=text.split(" ")), name=dataset
    )
    rubrix.load(dataset)
