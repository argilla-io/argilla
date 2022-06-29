import pytest

import rubrix as rb
from rubrix.client.sdk.commons.errors import BadRequestApiError, ValidationApiError
from rubrix.server.settings import settings


def test_log_records_with_multi_and_single_label_task(mocked_client):
    dataset = "test_log_records_with_multi_and_single_label_task"
    expected_inputs = ["This is a text"]

    rb.delete(dataset)
    records = [
        rb.TextClassificationRecord(
            id=0,
            inputs=expected_inputs,
            multi_label=False,
        ),
        rb.TextClassificationRecord(
            id=1,
            inputs=expected_inputs,
            multi_label=True,
        ),
    ]

    with pytest.raises(ValidationApiError):
        rb.log(
            records,
            name=dataset,
        )

    rb.log(records[0], name=dataset)
    with pytest.raises(Exception):
        rb.log(records[1], name=dataset)


def test_delete_and_create_for_different_task(mocked_client):
    dataset = "test_delete_and_create_for_different_task"
    text = "This is a text"

    rb.delete(dataset)
    rb.log(rb.TextClassificationRecord(id=0, inputs=text), name=dataset)
    rb.load(dataset)

    rb.delete(dataset)
    rb.log(
        rb.TokenClassificationRecord(id=0, text=text, tokens=text.split(" ")),
        name=dataset,
    )
    rb.load(dataset)


def test_search_keywords(mocked_client):
    dataset = "test_search_keywords"
    from datasets import load_dataset

    dataset_ds = load_dataset("Recognai/sentiment-banking", split="train")
    dataset_rb = rb.read_datasets(dataset_ds, task="TextClassification")

    rb.delete(dataset)
    rb.log(name=dataset, records=dataset_rb)

    ds = rb.load(dataset, query="lim*")
    df = ds.to_pandas()
    assert not df.empty
    assert "search_keywords" in df.columns
    top_keywords = set(
        [
            keyword
            for keywords in df.search_keywords.value_counts(sort=True, ascending=False)
            .index[:3]
            .tolist()
            for keyword in keywords
        ]
    )
    assert top_keywords == {"limits", "limited", "limit"}, top_keywords


def test_log_records_with_empty_metadata_list(mocked_client):
    dataset = "test_log_records_with_empty_metadata_list"

    rb.delete(dataset)
    expected_records = [
        rb.TextClassificationRecord(text="The input text", metadata={"emptyList": []}),
        rb.TextClassificationRecord(text="The input text", metadata={"emptyTuple": ()}),
        rb.TextClassificationRecord(text="The input text", metadata={"emptyDict": {}}),
        rb.TextClassificationRecord(text="The input text", metadata={"none": None}),
    ]
    rb.log(expected_records, name=dataset)

    df = rb.load(dataset)
    df = df.to_pandas()
    assert len(df) == len(expected_records)

    for meta in df.metadata.values.tolist():
        assert meta == {}


def test_logging_with_metadata_limits_exceeded(mocked_client):
    dataset = "test_logging_with_metadata_limits_exceeded"

    rb.delete(dataset)
    expected_record = rb.TextClassificationRecord(
        text="The input text",
        metadata={k: k for k in range(0, settings.metadata_fields_limit + 1)},
    )
    with pytest.raises(BadRequestApiError):
        rb.log(expected_record, name=dataset)

    expected_record.metadata = {k: k for k in range(0, settings.metadata_fields_limit)}
    rb.log(expected_record, name=dataset)

    expected_record.metadata["new_key"] = "value"
    with pytest.raises(BadRequestApiError):
        rb.log(expected_record, name=dataset)


def test_log_with_other_task(mocked_client):
    dataset = "test_log_with_other_task"

    rb.delete(dataset)
    record = rb.TextClassificationRecord(
        text="The input text",
    )
    rb.log(record, name=dataset)

    with pytest.raises(BadRequestApiError):
        rb.log(
            rb.TokenClassificationRecord(text="The text", tokens=["The", "text"]),
            name=dataset,
        )


def test_dynamics_metadata(mocked_client):
    dataset = "test_dynamics_metadata"
    rb.log(
        rb.TextClassificationRecord(text="This is a text", metadata={"a": "value"}),
        name=dataset,
    )

    rb.log(
        rb.TextClassificationRecord(text="Another text", metadata={"b": "value"}),
        name=dataset,
    )
