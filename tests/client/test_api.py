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

import rubrix as rb
from rubrix.client import api
from rubrix.client.api import InputValueError
from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.errors import (
    AlreadyExistsApiError,
    ForbiddenApiError,
    GenericApiError,
    NotFoundApiError,
    UnauthorizedApiError,
    ValidationApiError,
)
from rubrix.server.security import auth
from rubrix.server.tasks.text_classification import TextClassificationSearchResults
from tests.server.test_api import create_some_data_for_text_classification


@pytest.fixture
def mock_response_200(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 200 status code, emulating the correct login.
    """

    def mock_get(url, *args, **kwargs):
        if "/api/me" in url:
            return httpx.Response(status_code=200, json={"username": "booohh"})
        return httpx.Response(status_code=200)

    monkeypatch.setattr(httpx, "get", mock_get)


@pytest.fixture
def mock_response_500(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 500 status code, emulating an invalid state of the API error.
    """

    def mock_get(*args, **kwargs):
        return httpx.Response(status_code=500)

    monkeypatch.setattr(httpx, "get", mock_get)


@pytest.fixture
def mock_response_token_401(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 401 status code, emulating an invalid credentials error when using tokens to log in.
    Iterable structure to be able to pass the first 200 status code check
    """
    response_200 = httpx.Response(status_code=200)
    response_401 = httpx.Response(status_code=401)

    def mock_get(*args, **kwargs):
        if kwargs["url"] == "fake_url/api/me":
            return response_401
        elif kwargs["url"] == "fake_url/api/docs/spec.json":
            return response_200

    monkeypatch.setattr(httpx, "get", mock_get)


def test_init_correct(mock_response_200):
    """Testing correct default initalization

    It checks if the _client created is a RubrixClient object.
    """

    api.init()
    assert api.__ACTIVE_API__._client == AuthenticatedClient(
        base_url="http://localhost:6900", token="rubrix.apikey", timeout=60.0
    )
    assert api.__ACTIVE_API__._user == api.User(username="booohh")

    api.init(api_url="mock_url", api_key="mock_key", workspace="mock_ws", timeout=42)
    assert api.__ACTIVE_API__._client == AuthenticatedClient(
        base_url="mock_url",
        token="mock_key",
        timeout=42,
        headers={"X-Rubrix-Workspace": "mock_ws"},
    )


def test_init_incorrect(mock_response_500):
    """Testing incorrect default initalization

    It checks an Exception is raised with the correct message.
    """

    with pytest.raises(
        Exception,
        match="Rubrix server returned an error with http status: 500\nError details: \[\{'response': None\}\]",
    ):
        api.init()


def test_init_token_auth_fail(mock_response_token_401):
    """Testing initalization with failed authentication

    It checks an Exception is raised with the correct message.
    """
    with pytest.raises(UnauthorizedApiError):
        api.init(api_url="fake_url", api_key="422")


def test_init_evironment_url(mock_response_200, monkeypatch):
    """Testing initalization with api_url provided via environment variable

    It checks the url in the environment variable gets passed to client.
    """
    monkeypatch.setenv("RUBRIX_API_URL", "mock_url")
    monkeypatch.setenv("RUBRIX_API_KEY", "mock_key")
    monkeypatch.setenv("RUBRIX_WORKSPACE", "mock_workspace")
    api.init()

    assert api.__ACTIVE_API__._client == AuthenticatedClient(
        base_url="mock_url",
        token="mock_key",
        timeout=60,
        headers={"X-Rubrix-Workspace": "mock_workspace"},
    )


def test_trailing_slash(mock_response_200):
    """Testing initalization with provided api_url via environment variable and argument

    It checks the trailing slash is removed in all cases
    """
    api.init(api_url="http://mock.com/")
    assert api.__ACTIVE_API__._client.base_url == "http://mock.com"


def test_log_something(monkeypatch, mocked_client):
    dataset_name = "test-dataset"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    response = api.log(
        name=dataset_name,
        records=rb.TextClassificationRecord(inputs={"text": "This is a test"}),
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


def test_load_limits(mocked_client):
    dataset = "test_load_limits"
    api_ds_prefix = f"/api/datasets/{dataset}"
    mocked_client.delete(api_ds_prefix)

    create_some_data_for_text_classification(mocked_client, dataset, 50)

    limit_data_to = 10
    ds = api.load(name=dataset, limit=limit_data_to)
    assert isinstance(ds, pandas.DataFrame)
    assert len(ds) == limit_data_to

    ds = api.load(name=dataset, limit=limit_data_to)
    assert isinstance(ds, pandas.DataFrame)
    assert len(ds) == limit_data_to


def test_log_records_with_too_long_text(mocked_client):
    dataset_name = "test_log_records_with_too_long_text"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    item = rb.TextClassificationRecord(
        inputs={"text": "This is a toooooo long text\n" * 10000}
    )

    api.log([item], name=dataset_name)


def test_not_found_response(mocked_client):

    with pytest.raises(NotFoundApiError):
        api.load(name="not-found")


def test_log_without_name(mocked_client):
    with pytest.raises(
        api.InputValueError, match="Empty dataset name has been passed as argument."
    ):
        api.log(
            rb.TextClassificationRecord(
                inputs={"text": "This is a single record. Only this. No more."}
            ),
            name=None,
        )


def test_log_passing_empty_records_list(mocked_client):

    with pytest.raises(
        api.InputValueError, match="Empty record list has been passed as argument."
    ):
        api.log(records=[], name="ds")


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
def test_delete_with_errors(mocked_client, monkeypatch, status, error_type):
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
        api.delete("dataset")


@pytest.mark.parametrize(
    "records, dataset_class",
    [
        ("singlelabel_textclassification_records", rb.DatasetForTextClassification),
        ("multilabel_textclassification_records", rb.DatasetForTextClassification),
        ("tokenclassification_records", rb.DatasetForTokenClassification),
        ("text2text_records", rb.DatasetForText2Text),
    ],
)
def test_general_log_load(mocked_client, monkeypatch, request, records, dataset_class):
    dataset_names = [
        f"test_general_log_load_{dataset_class.__name__.lower()}_" + input_type
        for input_type in ["single", "list", "dataset"]
    ]
    for name in dataset_names:
        mocked_client.delete(f"/api/datasets/{name}")

    records = request.getfixturevalue(records)

    # log single records
    api.log(records[0], name=dataset_names[0])
    dataset = api.load(dataset_names[0], as_pandas=False)
    records[0].metrics = dataset[0].metrics
    assert dataset[0] == records[0]

    # log list of records
    api.log(records, name=dataset_names[1])
    dataset = api.load(dataset_names[1], as_pandas=False)
    # check if returned records can be converted to other formats
    assert isinstance(dataset.to_datasets(), datasets.Dataset)
    assert isinstance(dataset.to_pandas(), pd.DataFrame)
    assert len(dataset) == len(records)
    for record, expected in zip(dataset, records):
        expected.metrics = record.metrics
        assert record == expected

    # log dataset
    api.log(dataset_class(records), name=dataset_names[2])
    dataset = api.load(dataset_names[2], as_pandas=False)
    assert len(dataset) == len(records)
    for record, expected in zip(dataset, records):
        record.metrics = expected.metrics
        assert record == expected


def test_passing_wrong_iterable_data(mocked_client):
    dataset_name = "test_log_single_records"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    with pytest.raises(Exception, match="Unknown record type passed"):
        api.log({"a": "010", "b": 100}, name=dataset_name)


def test_log_with_generator(mocked_client, monkeypatch):
    dataset_name = "test_log_with_generator"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    def generator(items: int = 10) -> Iterable[rb.TextClassificationRecord]:
        for i in range(0, items):
            yield rb.TextClassificationRecord(id=i, inputs={"text": "The text data"})

    api.log(generator(), name=dataset_name)


def test_create_ds_with_wrong_name(mocked_client):
    dataset_name = "Test Create_ds_with_wrong_name"

    with pytest.raises(InputValueError):
        api.log(
            rb.TextClassificationRecord(
                inputs={"text": "The text data"},
            ),
            name=dataset_name,
        )


def test_delete_dataset(mocked_client):
    dataset_name = "test_delete_dataset"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    api.log(
        rb.TextClassificationRecord(
            id=0,
            inputs={"text": "The text data"},
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset_name,
    )
    api.load(name=dataset_name)
    api.delete(name=dataset_name)
    sleep(1)
    with pytest.raises(NotFoundApiError):
        api.load(name=dataset_name)


def test_log_with_wrong_name(mocked_client):
    with pytest.raises(InputValueError):
        api.log(name="Bad name", records=["whatever"])

    with pytest.raises(InputValueError):
        api.log(name="anotherWrongName", records=["whatever"])


def test_dataset_copy(mocked_client):
    dataset = "test_dataset_copy"
    dataset_copy = "new_dataset"
    other_workspace = "test_dataset_copy_ws"

    mocked_client.delete(f"/api/datasets/{dataset}")
    mocked_client.delete(f"/api/datasets/{dataset_copy}")
    mocked_client.delete(f"/api/datasets/{dataset_copy}?workspace={other_workspace}")

    api.log(
        rb.TextClassificationRecord(
            id=0,
            inputs="This is the record input",
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset,
    )
    api.copy(dataset, name_of_copy=dataset_copy)
    df = api.load(name=dataset)
    df_copy = api.load(name=dataset_copy)

    assert df.equals(df_copy)

    with pytest.raises(AlreadyExistsApiError):
        api.copy(dataset, name_of_copy=dataset_copy)
    with pytest.raises(NotFoundApiError, match=other_workspace):
        api.copy(dataset, name_of_copy=dataset_copy, workspace=other_workspace)


def test_dataset_copy_to_another_workspace(mocked_client):
    dataset = "test_dataset_copy_to_another_workspace"
    dataset_copy = "new_dataset"
    new_workspace = "my-fun-workspace"

    # Overrides the users dao config
    try:
        mocked_client.add_workspaces_to_rubrix_user([new_workspace])

        mocked_client.delete(f"/api/datasets/{dataset}")
        mocked_client.delete(f"/api/datasets/{dataset_copy}")
        mocked_client.delete(f"/api/datasets/{dataset_copy}?workspace={new_workspace}")

        api.log(
            rb.TextClassificationRecord(
                id=0,
                inputs="This is the record input",
                annotation_agent="test",
                annotation=["T"],
            ),
            name=dataset,
        )
        df = api.load(dataset)
        api.copy(dataset, name_of_copy=dataset_copy, workspace=new_workspace)
        api.set_workspace(new_workspace)
        df_copy = api.load(dataset_copy)
        assert df.equals(df_copy)

        with pytest.raises(AlreadyExistsApiError):
            api.copy(dataset_copy, name_of_copy=dataset_copy, workspace=new_workspace)
    finally:
        mocked_client.reset_rubrix_workspaces()
        api.init()  # reset workspace


def test_update_record(mocked_client):
    dataset = "test_update_record"
    mocked_client.delete(f"/api/datasets/{dataset}")

    expected_inputs = ["This is a text"]
    record = rb.TextClassificationRecord(
        id=0,
        inputs=expected_inputs,
        annotation_agent="test",
        annotation=["T"],
    )
    api.log(
        record,
        name=dataset,
    )

    df = api.load(name=dataset)
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["annotation"] == "T"
    # This record will replace the old one
    record = rb.TextClassificationRecord(
        id=0,
        inputs=expected_inputs,
    )

    api.log(
        record,
        name=dataset,
    )

    df = api.load(name=dataset)
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["annotation"] is None
    assert records[0]["annotation_agent"] is None


def test_text_classifier_with_inputs_list(mocked_client):
    dataset = "test_text_classifier_with_inputs_list"
    mocked_client.delete(f"/api/datasets/{dataset}")

    expected_inputs = ["A", "List", "of", "values"]
    api.log(
        rb.TextClassificationRecord(
            id=0,
            inputs=expected_inputs,
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset,
    )

    df = api.load(name=dataset)
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["inputs"]["text"] == expected_inputs


def test_load_with_ids_list(mocked_client):
    dataset = "test_load_with_ids_list"
    mocked_client.delete(f"/api/datasets/{dataset}")

    expected_data = 100
    create_some_data_for_text_classification(mocked_client, dataset, n=expected_data)
    ds = api.load(name=dataset, ids=[3, 5])
    assert len(ds) == 2


def test_load_with_query(mocked_client):
    dataset = "test_load_with_query"
    mocked_client.delete(f"/api/datasets/{dataset}")
    sleep(1)

    expected_data = 4
    create_some_data_for_text_classification(mocked_client, dataset, n=expected_data)
    ds = api.load(name=dataset, query="id:1")
    assert len(ds) == 1
    assert ds.id.iloc[0] == 1


@pytest.mark.parametrize("as_pandas", [True, False])
def test_load_as_pandas(mocked_client, as_pandas):
    dataset = "test_sorted_load"
    mocked_client.delete(f"/api/datasets/{dataset}")
    sleep(1)

    expected_data = 3
    create_some_data_for_text_classification(mocked_client, dataset, n=expected_data)

    # Check that the default value is True
    if as_pandas:
        records = api.load(name=dataset)
        assert isinstance(records, pandas.DataFrame)
        assert list(records.id) == [0, 1, 2, 3]
    else:
        records = api.load(name=dataset, as_pandas=False)
        assert isinstance(records, rb.DatasetForTextClassification)
        assert isinstance(records[0], rb.TextClassificationRecord)
        assert [record.id for record in records] == [0, 1, 2, 3]


def test_token_classification_spans(mocked_client):
    dataset = "test_token_classification_with_consecutive_spans"
    texto = "Esto es una prueba"
    item = api.TokenClassificationRecord(
        text=texto,
        tokens=texto.split(),
        prediction=[("test", 1, 2)],  # Inicio y fin son consecutivos
        prediction_agent="test",
    )
    with pytest.raises(
        Exception, match=r"Defined offset \[s\] is a misaligned entity mention"
    ):
        api.log(item, name=dataset)

    item.prediction = [("test", 0, 6)]
    with pytest.raises(
        Exception, match=r"Defined offset \[Esto e\] is a misaligned entity mention"
    ):
        api.log(item, name=dataset)

    item.prediction = [("test", 0, 4)]
    api.log(item, name=dataset)


def test_load_text2text(mocked_client):
    records = [
        rb.Text2TextRecord(
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
    api.delete(dataset)
    api.log(records, name=dataset)

    df = api.load(name=dataset)
    assert len(df) == 2


def test_client_workspace(mocked_client):
    try:
        ws = api.get_workspace()
        assert ws == "rubrix"

        api.set_workspace("")
        assert api.get_workspace() == ""

        with pytest.raises(Exception, match="Must provide a workspace"):
            api.set_workspace(None)

        # Mocking user
        api.__ACTIVE_API__._user.workspaces = ["a", "b"]

        with pytest.raises(Exception, match="Wrong provided workspace c"):
            api.set_workspace("c")

        api.set_workspace("rubrix")
        assert api.get_workspace() == "rubrix"
    finally:
        api.init()  # reset workspace


def test_load_sort(mocked_client):
    records = [
        rb.TextClassificationRecord(
            inputs="test text",
            id=i,
        )
        for i in ["1str", 1, 2, 11, "2str", "11str"]
    ]

    dataset = "test_load_sort"
    api.delete(dataset)
    api.log(records, name=dataset)

    # check sorting policies
    df = api.load(name=dataset)
    assert list(df.id) == [1, 11, "11str", "1str", 2, "2str"]
    df = api.load(name=dataset, ids=[1, 2, 11])
    assert list(df.id) == [1, 2, 11]
    df = api.load(name=dataset, ids=["1str", "2str", "11str"])
    assert list(df.id) == ["11str", "1str", "2str"]


def test_load_workspace_from_different_workspace(mocked_client):
    records = [
        rb.TextClassificationRecord(
            inputs="test text",
            id=i,
        )
        for i in ["1str", 1, 2, 11, "2str", "11str"]
    ]

    dataset = "test_load_workspace_from_different_workspace"
    workspace = api.get_workspace()
    try:
        api.set_workspace("")  # empty workspace
        api.delete(dataset)
        api.log(records, name=dataset)

        # check sorting policies
        df = api.load(name=dataset)
        assert list(df.id) == [1, 11, "11str", "1str", 2, "2str"]

        api.set_workspace(workspace)
        df = api.load(name=dataset)
        assert list(df.id) == [1, 11, "11str", "1str", 2, "2str"]
    finally:
        api.set_workspace(workspace)
