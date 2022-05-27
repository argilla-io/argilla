#  coding=utf-8
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

import datetime
from time import sleep
from typing import Iterable

import datasets
import httpx
import pandas
import pandas as pd
import pytest

import rubrix
from rubrix import (
    DatasetForText2Text,
    DatasetForTextClassification,
    DatasetForTokenClassification,
    Text2TextRecord,
    TextClassificationRecord,
)
from rubrix._constants import DEFAULT_API_KEY
from rubrix.client import RubrixClient, rubrix_client
from rubrix.client.sdk.commons.errors import (
    AlreadyExistsApiError,
    ForbiddenApiError,
    GenericApiError,
    NotFoundApiError,
    UnauthorizedApiError,
    ValidationApiError,
)
from rubrix.server.tasks.text_classification import TextClassificationSearchResults
from tests.server.test_api import create_some_data_for_text_classification

API_URL = api_url = "http://localhost:6900"


@pytest.fixture
def rb_client(mocked_client):

    return rubrix_client.RubrixClient(API_URL, api_key=DEFAULT_API_KEY)


def test_log_something(monkeypatch, mocked_client, rb_client):
    dataset_name = "test-dataset"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    response = rb_client.log(
        name=dataset_name,
        records=rubrix.TextClassificationRecord(inputs={"text": "This is a test"}),
    )

    assert response.processed == 1
    assert response.failed == 0

    response = mocked_client.post(
        f"/api/datasets/{dataset_name}/TextClassification:search"
    )
    assert response.status_code == 200, response.json()

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 1
    assert len(results.records) == 1
    assert results.records[0].inputs["text"] == "This is a test"


def test_load_limits(mocked_client, rb_client):
    dataset = "test_load_limits"
    api_ds_prefix = f"/api/datasets/{dataset}"
    mocked_client.delete(api_ds_prefix)

    create_some_data_for_text_classification(mocked_client, dataset, 50)

    limit_data_to = 10
    ds = rb_client.load(name=dataset, limit=limit_data_to)
    assert len(ds) == limit_data_to

    ds = rb_client.load(name=dataset, limit=limit_data_to)
    assert len(ds) == limit_data_to


def test_log_records_with_too_long_text(mocked_client, rb_client):
    dataset_name = "test_log_records_with_too_long_text"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    item = TextClassificationRecord(
        inputs={"text": "This is a toooooo long text\n" * 10000}
    )

    rb_client.log([item], name=dataset_name)


def test_not_found_response(rb_client):

    with pytest.raises(NotFoundApiError):
        rb_client.load(name="not-found")


def test_log_without_name(rb_client):
    with pytest.raises(
        rubrix_client.InputValueError,
        match="Empty project name has been passed as argument.",
    ):
        rb_client.log(
            TextClassificationRecord(
                inputs={"text": "This is a single record. Only this. No more."}
            ),
            name=None,
        )


def test_log_passing_empty_records_list(rb_client):

    with pytest.raises(
        rubrix_client.InputValueError,
        match="Empty record list has been passed as argument.",
    ):
        rb_client.log(records=[], name="ds")


@pytest.mark.parametrize(
    "status,error_type",
    [
        (401, UnauthorizedApiError),
        (403, ForbiddenApiError),
        (404, NotFoundApiError),
        (422, ValidationApiError),
        (500, GenericApiError),
    ],
)
def test_delete_with_errors(rb_client, monkeypatch, status, error_type):
    def send_mock_response_with_http_status(status: int):
        def inner(*args, **kwargs):
            return httpx.Response(
                status_code=status,
                json={"detail": {"code": "error:code", "params": {"message": "Mock"}}},
            )

        return inner

    with pytest.raises(error_type):
        monkeypatch.setattr(
            httpx, "delete", send_mock_response_with_http_status(status)
        )
        rb_client.delete("dataset")


@pytest.mark.parametrize(
    "records, dataset_class",
    [
        ("singlelabel_textclassification_records", DatasetForTextClassification),
        ("multilabel_textclassification_records", DatasetForTextClassification),
        ("tokenclassification_records", DatasetForTokenClassification),
        ("text2text_records", DatasetForText2Text),
    ],
)
def test_general_log_load(
    mocked_client, monkeypatch, request, records, dataset_class, rb_client
):
    dataset_names = [
        f"test_general_log_load_{dataset_class.__name__.lower()}_" + input_type
        for input_type in ["single", "list", "dataset"]
    ]
    for name in dataset_names:
        mocked_client.delete(f"/api/datasets/{name}")

    records = request.getfixturevalue(records)

    # log single records
    rb_client.log(records[0], name=dataset_names[0])
    dataset = rb_client.load(dataset_names[0])
    records[0].metrics = dataset[0].metrics
    assert dataset[0] == records[0]

    # log list of records
    rb_client.log(records, name=dataset_names[1])
    dataset = rb_client.load(dataset_names[1])
    # check if returned records can be converted to other formats
    assert isinstance(dataset.to_datasets(), datasets.Dataset)
    assert isinstance(dataset.to_pandas(), pd.DataFrame)
    assert len(dataset) == len(records)
    for record, expected in zip(dataset, records):
        expected.metrics = record.metrics
        assert record == expected

    # log dataset
    rb_client.log(dataset_class(records), name=dataset_names[2])
    dataset = rb_client.load(dataset_names[2])
    assert len(dataset) == len(records)
    for record, expected in zip(dataset, records):
        record.metrics = expected.metrics
        assert record == expected


def test_passing_wrong_iterable_data(mocked_client, rb_client):
    dataset_name = "test_log_single_records"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    with pytest.raises(Exception, match="Unknown record type passed"):
        rb_client.log({"a": "010", "b": 100}, name=dataset_name)


def test_log_with_generator(mocked_client, monkeypatch, rb_client):
    dataset_name = "test_log_with_generator"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    def generator(items: int = 10) -> Iterable[TextClassificationRecord]:
        for i in range(0, items):
            yield TextClassificationRecord(id=i, inputs={"text": "The text data"})

    rb_client.log(generator(), name=dataset_name)


def test_create_ds_with_wrong_name(rb_client):
    dataset_name = "Test Create_ds_with_wrong_name"

    with pytest.raises(ValidationApiError):
        rb_client.log(
            TextClassificationRecord(
                inputs={"text": "The text data"},
            ),
            name=dataset_name,
        )


def test_delete_dataset(mocked_client, rb_client):
    dataset_name = "test_delete_dataset"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    rb_client.log(
        TextClassificationRecord(
            id=0,
            inputs={"text": "The text data"},
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset_name,
    )
    rb_client.load(name=dataset_name)
    rb_client.delete(name=dataset_name)
    sleep(1)
    with pytest.raises(NotFoundApiError):
        rb_client.load(name=dataset_name)


def test_copy_dataset_to_another_workspace(mocked_client, rb_client):
    dataset = "test_copy_dataset_to_another_workspace"
    copy = "test_copy_dataset_to_another_workspace_copy"
    workspace = "test_copy_dataset_to_another_workspace-ws"

    rb_client.log(
        TextClassificationRecord(
            id=0,
            inputs="This is the record input",
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset,
    )
    ds = rb_client.load(name=dataset)
    df = ds.to_pandas()

    try:
        mocked_client.add_workspaces_to_rubrix_user([workspace])
        mocked_client.delete(f"/api/datasets/{copy}?workspace={workspace}")

        new_rb_client = RubrixClient(API_URL, api_key=DEFAULT_API_KEY)
        new_rb_client.copy(dataset, target=copy, target_workspace=workspace)
        new_rb_client.set_workspace(workspace)
        ds_copy = new_rb_client.load(copy)
        df_copy = df_copy = ds.to_pandas()
        assert df.equals(df_copy)

        with pytest.raises(AlreadyExistsApiError):
            new_rb_client.copy(copy, target=copy, target_workspace=workspace)
    finally:
        mocked_client.reset_rubrix_workspaces()


def test_dataset_copy(mocked_client, rb_client):
    dataset = "test_dataset_copy"
    dataset_copy = "test_dataset_copy_new"

    mocked_client.delete(f"/api/datasets/{dataset}")
    mocked_client.delete(f"/api/datasets/{dataset_copy}")

    rb_client.log(
        TextClassificationRecord(
            id=0,
            inputs="This is the record input",
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset,
    )
    rb_client.copy(dataset, target=dataset_copy)
    df, df_copy = rb_client.load(name=dataset), rb_client.load(name=dataset_copy)
    df, df_copy = df.to_pandas(), df_copy.to_pandas()

    assert df.equals(df_copy)

    with pytest.raises(AlreadyExistsApiError):
        rb_client.copy(dataset, target=dataset_copy)


def test_update_record(mocked_client, rb_client):
    dataset = "test_update_record"
    mocked_client.delete(f"/api/datasets/{dataset}")

    expected_inputs = ["This is a text"]
    record = TextClassificationRecord(
        id=0,
        inputs=expected_inputs,
        annotation_agent="test",
        annotation=["T"],
    )
    rb_client.log(
        record,
        name=dataset,
    )

    ds = rb_client.load(name=dataset)
    df = ds.to_pandas()
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["annotation"] == "T"
    # This record will replace the old one
    record = TextClassificationRecord(
        id=0,
        inputs=expected_inputs,
    )

    rb_client.log(
        record,
        name=dataset,
    )

    ds = rb_client.load(name=dataset)
    df = ds.to_pandas()
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["annotation"] is None
    assert records[0]["annotation_agent"] is None


def test_text_classifier_with_inputs_list(mocked_client, rb_client):
    dataset = "test_text_classifier_with_inputs_list"
    mocked_client.delete(f"/api/datasets/{dataset}")

    expected_inputs = ["A", "List", "of", "values"]
    rb_client.log(
        TextClassificationRecord(
            id=0,
            inputs=expected_inputs,
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset,
    )

    ds = rb_client.load(name=dataset)
    df = ds.to_pandas()
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["inputs"]["text"] == expected_inputs


def test_load_with_ids_list(mocked_client, rb_client):
    dataset = "test_load_with_ids_list"
    mocked_client.delete(f"/api/datasets/{dataset}")

    expected_data = 100
    create_some_data_for_text_classification(mocked_client, dataset, n=expected_data)
    ds = rb_client.load(name=dataset, ids=[3, 5])
    assert len(ds) == 2


def test_load_with_query(mocked_client, rb_client):
    dataset = "test_load_with_query"
    mocked_client.delete(f"/api/datasets/{dataset}")
    sleep(1)

    expected_data = 4
    create_some_data_for_text_classification(mocked_client, dataset, n=expected_data)
    df = rb_client.load(name=dataset, query="id:1")
    df = df.to_pandas()
    assert len(df) == 1
    assert df.id.iloc[0] == 1


def test_load_as_pandas(mocked_client, rb_client):
    dataset = "test_sorted_load"
    mocked_client.delete(f"/api/datasets/{dataset}")
    sleep(1)

    expected_data = 3
    create_some_data_for_text_classification(mocked_client, dataset, n=expected_data)

    records = rb_client.load(name=dataset)
    assert isinstance(records, DatasetForTextClassification)
    assert isinstance(records[0], TextClassificationRecord)
    assert [record.id for record in records] == [0, 1, 2, 3]


def test_token_classification_spans(rb_client):
    dataset = "test_token_classification_with_consecutive_spans"
    texto = "Esto es una prueba"
    item = rubrix.TokenClassificationRecord(
        text=texto,
        tokens=texto.split(),
        prediction=[("test", 1, 2)],  # Inicio y fin son consecutivos
        prediction_agent="test",
    )
    with pytest.raises(
        Exception, match=r"Defined offset \[s\] is a misaligned entity mention"
    ):
        rb_client.log(item, name=dataset)

    item.prediction = [("test", 0, 6)]
    with pytest.raises(
        Exception, match=r"Defined offset \[Esto e\] is a misaligned entity mention"
    ):
        rb_client.log(item, name=dataset)

    item.prediction = [("test", 0, 4)]
    rb_client.log(item, name=dataset)


def test_load_text2text(rb_client):
    records = [
        Text2TextRecord(
            text="test text",
            prediction=["test prediction"],
            annotation="test annotation",
            prediction_agent="test_model",
            annotation_agent="test_annotator",
            id=i,
            metadata={"metadata": "test"},
            status="Default",
            event_timestamp=datetime.datetime(2000, 1, 1),
        )
        for i in range(0, 2)
    ]

    dataset = "test_load_text2text"
    rb_client.delete(dataset)
    rb_client.log(records, name=dataset)

    df = rb_client.load(name=dataset)
    assert len(df) == 2


def test_client_workspace(rb_client):
    ws = rb_client.active_workspace
    assert ws == "rubrix"

    rb_client.__current_user__.workspaces = ["rubrix", "other-workspace"]

    rb_client.set_workspace("other-workspace")
    assert rb_client.active_workspace == "other-workspace"

    with pytest.raises(Exception, match="Must provide a workspace"):
        rb_client.set_workspace(None)

    # Mocking user
    rb_client.__current_user__.workspaces = ["a", "b"]

    with pytest.raises(Exception, match="Wrong provided workspace c"):
        rb_client.set_workspace("c")

    rb_client.set_workspace("rubrix")
    assert rb_client.active_workspace == "rubrix"


def test_load_sort(rb_client):
    records = [
        TextClassificationRecord(
            inputs="test text",
            id=i,
        )
        for i in ["1str", 1, 2, 11, "2str", "11str"]
    ]

    dataset = "test_load_sort"
    rb_client.delete(dataset)
    rb_client.log(records, name=dataset)

    # check sorting policies
    df = rb_client.load(name=dataset)
    df = df.to_pandas()
    assert list(df.id) == [1, 11, "11str", "1str", 2, "2str"]
    df = rb_client.load(name=dataset, ids=[1, 2, 11])
    df = df.to_pandas()
    assert list(df.id) == [1, 2, 11]
    df = rb_client.load(name=dataset, ids=["1str", "2str", "11str"])
    df = df.to_pandas()
    assert list(df.id) == ["11str", "1str", "2str"]
