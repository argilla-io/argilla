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

from typing import TYPE_CHECKING

import argilla_v1 as rg
import pytest
from argilla_server.settings import settings
from argilla_v1.client.api import load, log
from argilla_v1.client.client import Argilla
from argilla_v1.client.datasets import read_datasets
from argilla_v1.client.models import TextClassificationRecord, TokenClassificationRecord
from argilla_v1.client.sdk.commons.errors import (
    BadRequestApiError,
    GenericApiError,
    ValidationApiError,
)
from argilla_v1.client.singleton import init

from tests.factories import WorkspaceFactory
from tests.integration.utils import delete_ignoring_errors

if TYPE_CHECKING:
    from argilla_server.models import User


def test_log_records_with_multi_and_single_label_task(api: Argilla):
    dataset = "test_log_records_with_multi_and_single_label_task"
    expected_inputs = ["This is a text"]

    delete_ignoring_errors(dataset)
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

    with pytest.raises(ValidationApiError):
        api.log(
            records,
            name=dataset,
        )

    api.log(records[0], name=dataset)
    with pytest.raises(Exception):
        api.log(records[1], name=dataset)


def test_delete_and_create_for_different_task(api: Argilla):
    dataset = "test_delete_and_create_for_different_task"
    text = "This is a text"

    delete_ignoring_errors(dataset)
    api.log(TextClassificationRecord(id=0, inputs=text), name=dataset)
    api.load(dataset)

    delete_ignoring_errors(dataset)
    api.log(TokenClassificationRecord(id=0, text=text, tokens=text.split(" ")), name=dataset)
    api.load(dataset)


def test_similarity_search_in_python_client(api: Argilla):
    dataset = "test_similarity_search_in_python_client"
    text = "This is a text"
    vectors = {"my_bert": [1, 2, 3, 4]}

    delete_ignoring_errors(dataset)
    api.log(TextClassificationRecord(id=0, inputs=text, vectors=vectors), name=dataset)
    ds = api.load(dataset, vector=("my_bert", [1, 1, 1, 1]))
    assert len(ds) == 1

    api.log(TextClassificationRecord(id=1, inputs=text, vectors={"my_bert_2": [1, 2, 3, 4]}), name=dataset)
    ds = api.load(dataset, vector=("my_bert_2", [1, 1, 1, 1]))
    assert len(ds) == 1
    with pytest.raises(
        BadRequestApiError,
        match="Cannot create more than 5 kind of vectors per dataset",
    ):
        api.log(
            TextClassificationRecord(
                id=3,
                inputs=text,
                vectors={"a": [1.0], "b": [1.0], "c": [1.0], "d": [1.0], "e": [1.0]},
            ),
            name=dataset,
        )


def test_log_data_with_vectors_and_update_ok(api: Argilla):
    dataset = "test_log_data_with_vectors_and_update_ok"
    text = "This is a text"
    delete_ignoring_errors(dataset)

    records = [
        TextClassificationRecord(
            id=i,
            inputs=text,
            vectors={"text": [i] * 5},
        )
        for i in range(1, 10)
    ]

    api.log(records=records, name=dataset)
    ds = api.load(
        dataset,
        vector=(
            "text",
            [3, 3, 2, 3, 3],  # the first expected records should be the id=3
        ),
        limit=5,
    )

    assert len(ds) == 5
    assert ds[0].id == 3


def test_log_data_with_vectors_and_update_ko(argilla_user: "User"):
    dataset = "test_log_data_with_vectors_and_update_ko"
    text = "This is a text"
    vectors = {"my_bert": [1, 2, 3, 4]}

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    delete_ignoring_errors(dataset)
    log(TextClassificationRecord(id=0, inputs=text, vectors=vectors), name=dataset)
    load(dataset)

    updated_vectors = {"my_bert": [2, 3, 5]}
    with pytest.raises(GenericApiError):
        log(TextClassificationRecord(id=0, text=text, vectors=updated_vectors), name=dataset)


@pytest.mark.asyncio
async def test_log_data_in_several_workspaces(owner: "User"):
    dataset_name = "test_log_data_in_several_workspaces"
    text = "This is a text"

    workspace = await WorkspaceFactory.create()
    other_workspace = await WorkspaceFactory.create()

    client = Argilla(api_key=owner.api_key, workspace=workspace.name)

    for ws in [workspace, other_workspace]:
        client.set_workspace(ws.name)
        client.delete(dataset_name)

    client.set_workspace(workspace.name)
    client.log(rg.TextClassificationRecord(id=0, inputs=text), name=dataset_name)

    client.set_workspace(other_workspace.name)
    client.log(rg.TextClassificationRecord(id=1, inputs=text), name=dataset_name)

    ds = client.load(dataset_name)
    assert len(ds) == 1

    client.set_workspace(workspace.name)

    ds = client.load(dataset_name)
    assert len(ds) == 1


def test_search_keywords(argilla_user: "User"):
    dataset = "test_search_keywords"
    from datasets import load_dataset

    dataset_ds = load_dataset("Recognai/sentiment-banking", split="train")
    dataset_rb = read_datasets(dataset_ds, task="TextClassification")

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    delete_ignoring_errors(dataset)
    log(name=dataset, records=dataset_rb)

    ds = load(dataset, query="lim*")
    df = ds.to_pandas()
    assert not df.empty
    assert "search_keywords" in df.columns
    top_keywords = set(
        [
            keyword
            for keywords in df.search_keywords.value_counts(sort=True, ascending=False).index[:3].tolist()
            for keyword in keywords
        ]
    )
    assert top_keywords == {"limits", "limited", "limit"}, top_keywords


def test_log_records_with_empty_metadata_list(argilla_user: "User"):
    dataset = "test_log_records_with_empty_metadata_list"

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    delete_ignoring_errors(dataset)
    expected_records = [
        TextClassificationRecord(text="The input text", metadata={"emptyList": []}),
        TextClassificationRecord(text="The input text", metadata={"emptyTuple": ()}),
        TextClassificationRecord(text="The input text", metadata={"emptyDict": {}}),
        TextClassificationRecord(text="The input text", metadata={"none": None}),
    ]
    log(expected_records, name=dataset)

    df = load(dataset)
    df = df.to_pandas()
    assert len(df) == len(expected_records)

    for meta in df.metadata.values.tolist():
        assert meta == {}


def test_logging_with_metadata_limits_exceeded(argilla_user: "User"):
    dataset = "test_logging_with_metadata_limits_exceeded"

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    delete_ignoring_errors(dataset)

    expected_record = TextClassificationRecord(
        text="The input text",
        metadata={k: f"this is a string {k}" for k in range(0, settings.metadata_fields_limit + 1)},
    )
    with pytest.raises(BadRequestApiError):
        log(expected_record, name=dataset)

    expected_record.metadata = {k: f"This is a string {k}" for k in range(0, settings.metadata_fields_limit)}
    # Dataset creation with data
    log(expected_record, name=dataset)
    # This call will check already included fields
    log(expected_record, name=dataset)

    expected_record.metadata["new_key"] = "value"
    with pytest.raises(BadRequestApiError):
        log(expected_record, name=dataset)


def test_log_with_other_task(argilla_user: "User"):
    dataset = "test_log_with_other_task"

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    delete_ignoring_errors(dataset)
    record = TextClassificationRecord(text="The input text")
    log(record, name=dataset)

    with pytest.raises(BadRequestApiError):
        log(TokenClassificationRecord(text="The text", tokens=["The", "text"]), name=dataset)


def test_dynamics_metadata(argilla_user: "User"):
    dataset = "test_dynamics_metadata"

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    log(TextClassificationRecord(text="This is a text", metadata={"a": "value"}), name=dataset)
    log(TextClassificationRecord(text="Another text", metadata={"b": "value"}), name=dataset)


def test_log_with_bulk_error(argilla_user: "User"):
    dataset = "test_log_with_bulk_error"

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    delete_ignoring_errors(dataset)
    try:
        log(
            [
                TextClassificationRecord(id=0, text="This is an special text", metadata={"key": 1}),
                TextClassificationRecord(id=1, text="This is an special text", metadata={"key": "wrong-value"}),
            ],
            name=dataset,
        )
    except BadRequestApiError as error:
        assert error.ctx["code"] == "argilla.api.errors::BulkDataError"
        assert error.ctx["params"]["message"] == "Cannot log data in dataset argilla.test_log_with_bulk_error"
        assert error.ctx["params"]["errors"][0]["caused_by"] == {
            "type": "illegal_argument_exception",
            "reason": 'For input string: "wrong-value"',
        }
