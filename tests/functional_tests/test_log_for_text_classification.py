import pytest

import rubrix
from rubrix import TextClassificationRecord, TokenClassificationRecord
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
