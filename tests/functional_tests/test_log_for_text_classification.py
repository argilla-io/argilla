import pytest

import rubrix
from rubrix import TextClassificationRecord, TokenClassificationRecord
from rubrix.server.commons.settings import settings
from rubrix.server.tasks.commons import MetadataLimitExceededError
from tests.server.test_helpers import client, mocking_client


def test_log_records_with_multi_and_single_label_task(monkeypatch):
    mocking_client(monkeypatch, client)
    dataset = "test_log_records_with_multi_and_single_label_task"
    expected_inputs = ["This is a text"]

    rubrix.delete(dataset)
    records = [
        TextClassificationRecord(
            id=0,
            inputs=expected_inputs,
            multi_label=False,
        ),
        TextClassificationRecord(
            id=1,
            inputs=expected_inputs,
            multi_label=True,
        ),
    ]

    with pytest.raises(
        Exception,
        match="msg='All records must be single/multi labelled'",
    ):
        rubrix.log(
            records,
            name=dataset,
        )

    rubrix.log(records[0], name=dataset)
    with pytest.raises(Exception):
        rubrix.log(records[1], name=dataset)


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


def test_log_records_with_empty_metadata_list(monkeypatch):
    mocking_client(monkeypatch, client)
    dataset = "test_log_records_with_empty_metadata_list"

    rubrix.delete(dataset)
    expected_records = [
        TextClassificationRecord(inputs="The input text", metadata={"emptyList": []}),
        TextClassificationRecord(inputs="The input text", metadata={"emptyTuple": ()}),
        TextClassificationRecord(inputs="The input text", metadata={"emptyDict": {}}),
        TextClassificationRecord(inputs="The input text", metadata={"none": None}),
    ]
    rubrix.log(expected_records, name=dataset)

    df = rubrix.load(dataset)
    assert len(df) == len(expected_records)

    for meta in df.metadata.values.tolist():
        assert meta == {}


def test_logging_with_metadata_limits_exceeded(monkeypatch):
    mocking_client(monkeypatch, client)
    dataset = "test_delete_and_create_for_different_task"

    rubrix.delete(dataset)
    expected_record = TextClassificationRecord(
        inputs="The input text",
        metadata={k: k for k in range(0, settings.metadata_fields_limit + 1)},
    )
    with pytest.raises(MetadataLimitExceededError):
        rubrix.log(expected_record, name=dataset)

    expected_record.metadata = {k: k for k in range(0, settings.metadata_fields_limit)}
    rubrix.log(expected_record, name=dataset)

    expected_record.metadata["new_key"] = "value"
    with pytest.raises(MetadataLimitExceededError):
        rubrix.log(expected_record, name=dataset)
