#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pytest

import argilla as ar
from argilla.client.sdk.commons.errors import (
    BadRequestApiError,
    GenericApiError,
    ValidationApiError,
)
from argilla.server.settings import settings
from tests.client.conftest import SUPPORTED_VECTOR_SEARCH, supported_vector_search
from tests.helpers import SecuredClient


def test_log_records_with_multi_and_single_label_task(mocked_client):
    dataset = "test_log_records_with_multi_and_single_label_task"
    expected_inputs = ["This is a text"]

    ar.delete(dataset)
    records = [
        ar.TextClassificationRecord(
            id=0,
            inputs=expected_inputs,
            multi_label=False,
        ),
        ar.TextClassificationRecord(
            id=1,
            inputs=expected_inputs,
            multi_label=True,
        ),
    ]

    with pytest.raises(ValidationApiError):
        ar.log(
            records,
            name=dataset,
        )

    ar.log(records[0], name=dataset)
    with pytest.raises(Exception):
        ar.log(records[1], name=dataset)


def test_delete_and_create_for_different_task(mocked_client):
    dataset = "test_delete_and_create_for_different_task"
    text = "This is a text"

    ar.delete(dataset)
    ar.log(ar.TextClassificationRecord(id=0, inputs=text), name=dataset)
    ar.load(dataset)

    ar.delete(dataset)
    ar.log(
        ar.TokenClassificationRecord(id=0, text=text, tokens=text.split(" ")),
        name=dataset,
    )
    ar.load(dataset)


@pytest.mark.skipif(
    condition=not SUPPORTED_VECTOR_SEARCH,
    reason="Vector search not supported",
)
def test_log_data_with_embeddings_and_update_ok(mocked_client: SecuredClient):
    dataset = "test_log_data_with_embeddings_and_update_ok"
    text = "This is a text"
    embeddings = {"my_bert": {"vector": [1, 2, 3, 4]}}

    ar.delete(dataset)
    ar.log(
        ar.TextClassificationRecord(id=0, inputs=text, embeddings=embeddings),
        name=dataset,
    )
    ar.load(dataset)

    updated_embeddings = {"my_bert": {"vector": [2, 3, 5, 5]}}

    ar.log(
        ar.TextClassificationRecord(id=0, text=text, embeddings=updated_embeddings),
        name=dataset,
    )
    ar.load(dataset)

    dataset_rg = ar.load(dataset)
    print(dataset_rg._records[0])
    assert dataset_rg._records[0].id == 0
    assert dataset_rg._records[0].embeddings["my_bert"]["vector"] == [
        "2.0",
        "3.0",
        "5.0",
        "5.0",
    ]  # will be corrected after I fix the returned list type issue @frascuchon


@pytest.mark.skipif(
    condition=not SUPPORTED_VECTOR_SEARCH,
    reason="Vector search not supported",
)
def test_log_data_with_embeddings_and_update_ko(mocked_client: SecuredClient):
    dataset = "test_log_data_with_embeddings_and_update_ko"
    text = "This is a text"
    embeddings = {"my_bert": {"vector": [1, 2, 3, 4]}}

    ar.delete(dataset)
    ar.log(
        ar.TextClassificationRecord(id=0, inputs=text, embeddings=embeddings),
        name=dataset,
    )
    ar.load(dataset)

    updated_embeddings = {"my_bert": {"vector": [2, 3, 5]}}
    with pytest.raises(GenericApiError):
        ar.log(
            ar.TextClassificationRecord(id=0, text=text, embeddings=updated_embeddings),
            name=dataset,
        )


def test_log_data_in_several_workspaces(mocked_client: SecuredClient):

    workspace = "test-ws"
    dataset = "test_log_data_in_several_workspaces"
    text = "This is a text"

    mocked_client.add_workspaces_to_argilla_user([workspace])

    curr_ws = ar.get_workspace()
    for ws in [curr_ws, workspace]:
        ar.set_workspace(ws)
        ar.delete(dataset)

    ar.set_workspace(curr_ws)
    ar.log(ar.TextClassificationRecord(id=0, inputs=text), name=dataset)

    ar.set_workspace(workspace)
    ar.log(ar.TextClassificationRecord(id=1, inputs=text), name=dataset)
    ds = ar.load(dataset)
    assert len(ds) == 1

    ar.set_workspace(curr_ws)
    ds = ar.load(dataset)
    assert len(ds) == 1


def test_search_keywords(mocked_client):
    dataset = "test_search_keywords"
    from datasets import load_dataset

    dataset_ds = load_dataset("Recognai/sentiment-banking", split="train")
    dataset_rb = ar.read_datasets(dataset_ds, task="TextClassification")

    ar.delete(dataset)
    ar.log(name=dataset, records=dataset_rb)

    ds = ar.load(dataset, query="lim*")
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

    ar.delete(dataset)
    expected_records = [
        ar.TextClassificationRecord(text="The input text", metadata={"emptyList": []}),
        ar.TextClassificationRecord(text="The input text", metadata={"emptyTuple": ()}),
        ar.TextClassificationRecord(text="The input text", metadata={"emptyDict": {}}),
        ar.TextClassificationRecord(text="The input text", metadata={"none": None}),
    ]
    ar.log(expected_records, name=dataset)

    df = ar.load(dataset)
    df = df.to_pandas()
    assert len(df) == len(expected_records)

    for meta in df.metadata.values.tolist():
        assert meta == {}


def test_logging_with_metadata_limits_exceeded(mocked_client):
    dataset = "test_logging_with_metadata_limits_exceeded"

    ar.delete(dataset)

    expected_record = ar.TextClassificationRecord(
        text="The input text",
        metadata={
            k: f"this is a string {k}"
            for k in range(0, settings.metadata_fields_limit + 1)
        },
    )
    with pytest.raises(BadRequestApiError):
        ar.log(expected_record, name=dataset)

    expected_record.metadata = {
        k: f"This is a string {k}" for k in range(0, settings.metadata_fields_limit)
    }
    # Dataset creation with data
    ar.log(expected_record, name=dataset)
    # This call will check already included fields
    ar.log(expected_record, name=dataset)

    expected_record.metadata["new_key"] = "value"
    with pytest.raises(BadRequestApiError):
        ar.log(expected_record, name=dataset)


def test_log_with_other_task(mocked_client):
    dataset = "test_log_with_other_task"

    ar.delete(dataset)
    record = ar.TextClassificationRecord(
        text="The input text",
    )
    ar.log(record, name=dataset)

    with pytest.raises(BadRequestApiError):
        ar.log(
            ar.TokenClassificationRecord(text="The text", tokens=["The", "text"]),
            name=dataset,
        )


def test_dynamics_metadata(mocked_client):
    dataset = "test_dynamics_metadata"
    ar.log(
        ar.TextClassificationRecord(text="This is a text", metadata={"a": "value"}),
        name=dataset,
    )

    ar.log(
        ar.TextClassificationRecord(text="Another text", metadata={"b": "value"}),
        name=dataset,
    )
