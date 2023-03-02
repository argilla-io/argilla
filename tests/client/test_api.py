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
import concurrent.futures
import datetime
from time import sleep
from typing import Any, Iterable

import argilla as rg
import datasets
import httpx
import pandas as pd
import pytest
from argilla._constants import (
    _OLD_WORKSPACE_HEADER_NAME,
    DEFAULT_API_KEY,
    WORKSPACE_HEADER_NAME,
)
from argilla.client import api
from argilla.client.client import Argilla
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.commons.errors import (
    AlreadyExistsApiError,
    BaseClientError,
    ForbiddenApiError,
    GenericApiError,
    HttpResponseError,
    InputValueError,
    NotFoundApiError,
    UnauthorizedApiError,
    ValidationApiError,
)
from argilla.client.sdk.users import api as users_api
from argilla.client.sdk.users.models import User
from argilla.server.apis.v0.models.text_classification import (
    TextClassificationSearchResults,
)

from tests.helpers import SecuredClient
from tests.server.test_api import create_some_data_for_text_classification


@pytest.fixture
def mock_response_200(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 200 status code, emulating the correct login.
    """

    def mock_get(*args, **kwargs):
        return User(username="booohh")

    monkeypatch.setattr(users_api, "whoami", mock_get)


@pytest.fixture
def mock_response_500(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 500 status code, emulating an invalid state of the API error.
    """

    def mock_get(*args, **kwargs):
        raise GenericApiError("Mock error")

    monkeypatch.setattr(users_api, "whoami", mock_get)


@pytest.fixture
def mock_response_token_401(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 401 status code, emulating an invalid credentials error when using tokens to log in.
    Iterable structure to be able to pass the first 200 status code check
    """

    def mock_get(*args, **kwargs):
        if kwargs["url"] == "fake_url/api/me":
            raise UnauthorizedApiError()
        elif kwargs["url"] == "fake_url/api/docs/spec.json":
            return User(username="booohh")

    monkeypatch.setattr(users_api, "whoami", mock_get)


def test_init_correct(mock_response_200):
    """Testing correct default initialization

    It checks if the _client created is a argillaClient object.
    """

    assert api.active_api().http_client == AuthenticatedClient(
        base_url="http://localhost:6900",
        token=DEFAULT_API_KEY,
        timeout=60.0,
    )

    assert api.active_api().user == User(username="booohh")

    api.init(
        api_url="mock_url",
        api_key="mock_key",
        workspace="mock_ws",
        timeout=42,
    )
    assert api.active_api().http_client == AuthenticatedClient(
        base_url="mock_url",
        token="mock_key",
        timeout=42,
        headers={
            WORKSPACE_HEADER_NAME: "mock_ws",
            _OLD_WORKSPACE_HEADER_NAME: "mock_ws",
        },
    )


def test_init_environment_url(mock_response_200, monkeypatch):
    """Testing initialization with api_url provided via environment variable

    It checks the url in the environment variable gets passed to client.
    """
    monkeypatch.setenv("ARGILLA_API_URL", "mock_url")
    monkeypatch.setenv("ARGILLA_API_KEY", "mock_key")
    monkeypatch.setenv("ARGILLA_WORKSPACE", "mock_workspace")
    api.init()

    assert api.active_api()._client == AuthenticatedClient(
        base_url="mock_url",
        token="mock_key",
        timeout=60,
        headers={
            WORKSPACE_HEADER_NAME: "mock_workspace",
            _OLD_WORKSPACE_HEADER_NAME: "mock_workspace",
        },
    )


def test_trailing_slash(mock_response_200):
    """Testing initialization with provided api_url via environment variable and argument

    It checks the trailing slash is removed in all cases
    """
    api.init(api_url="http://mock.com/")
    assert api.active_api()._client.base_url == "http://mock.com"


def test_log_something(monkeypatch, mocked_client):
    dataset_name = "test-dataset"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    response = api.log(
        name=dataset_name,
        records=rg.TextClassificationRecord(inputs={"text": "This is a test"}),
    )

    assert response.processed == 1
    assert response.failed == 0

    response = mocked_client.post(f"/api/datasets/{dataset_name}/TextClassification:search")
    assert response.status_code == 200, response.json()

    results = TextClassificationSearchResults.parse_obj(response.json())
    assert results.total == 1
    assert len(results.records) == 1
    assert results.records[0].inputs["text"] == "This is a test"


def test_load_limits(mocked_client, supported_vector_search):
    dataset = "test_load_limits"
    api_ds_prefix = f"/api/datasets/{dataset}"
    mocked_client.delete(api_ds_prefix)

    create_some_data_for_text_classification(
        mocked_client,
        dataset,
        n=50,
        with_vectors=supported_vector_search,
    )

    limit_data_to = 10
    ds = api.load(name=dataset, limit=limit_data_to)
    assert len(ds) == limit_data_to

    ds = api.load(name=dataset, limit=limit_data_to)
    assert len(ds) == limit_data_to


def test_log_records_with_too_long_text(mocked_client):
    dataset_name = "test_log_records_with_too_long_text"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    item = rg.TextClassificationRecord(inputs={"text": "This is a toooooo long text\n" * 10000})

    api.log([item], name=dataset_name)


def test_not_found_response(mocked_client):
    with pytest.raises(NotFoundApiError):
        api.load(name="not-found")


def test_log_without_name(mocked_client):
    with pytest.raises(
        InputValueError,
        match="Empty dataset name has been passed as argument.",
    ):
        api.log(
            rg.TextClassificationRecord(inputs={"text": "This is a single record. Only this. No more."}),
            name=None,
        )


def test_log_passing_empty_records_list(mocked_client):
    with pytest.raises(
        InputValueError,
        match="Empty record list has been passed as argument.",
    ):
        api.log(records=[], name="ds")


def test_log_deprecated_chunk_size(mocked_client):
    dataset_name = "test_log_deprecated_chunk_size"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    record = rg.TextClassificationRecord(text="My text")
    with pytest.warns(FutureWarning, match="`chunk_size`.*`batch_size`"):
        api.log(records=[record], name=dataset_name, chunk_size=100)


def test_log_background(mocked_client):
    """Verify that logs can be delayed via the background parameter."""
    dataset_name = "test_log_background"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    # Log in the background, and extract the future
    sample_text = "Sample text for testing"
    future = api.log(
        rg.TextClassificationRecord(text=sample_text),
        name=dataset_name,
        background=True,
    )
    assert isinstance(future, concurrent.futures.Future)
    # Log the record to argilla
    try:
        future.result()
    finally:
        future.cancel()

    # The dataset now exists and holds one record
    dataset = api.load(dataset_name)
    assert len(dataset) == 1
    assert dataset[0].text == sample_text


def test_log_background_with_error(
    mocked_client: SecuredClient,
    monkeypatch: Any,
):
    dataset_name = "test_log_background_with_error"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    # Log in the background, and extract the future
    sample_text = "Sample text for testing"

    def raise_http_error(*args, **kwargs):
        raise httpx.ConnectError(
            "Mock error",
            request=None,
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", raise_http_error)

    future = api.log(
        rg.TextClassificationRecord(text=sample_text),
        name=dataset_name,
        background=True,
    )

    with pytest.raises(BaseClientError):
        try:
            future.result()
        finally:
            future.cancel()


@pytest.mark.parametrize(
    "status,error_type",
    [
        (401, UnauthorizedApiError),
        (403, ForbiddenApiError),
        (404, NotFoundApiError),
        (422, ValidationApiError),
        (500, GenericApiError),
        (413, HttpResponseError),
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
        monkeypatch.setattr(httpx, "delete", send_mock_response_with_http_status(status))
        api.delete("dataset")


@pytest.mark.parametrize(
    "records, dataset_class",
    [
        ("singlelabel_textclassification_records", rg.DatasetForTextClassification),
        ("multilabel_textclassification_records", rg.DatasetForTextClassification),
        ("tokenclassification_records", rg.DatasetForTokenClassification),
        ("text2text_records", rg.DatasetForText2Text),
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
    dataset = api.load(dataset_names[0])
    records[0].metrics = dataset[0].metrics
    assert dataset[0] == records[0]

    # log list of records
    api.log(records, name=dataset_names[1])
    dataset = api.load(dataset_names[1])
    # check if returned records can be converted to other formats
    assert isinstance(dataset.to_datasets(), datasets.Dataset)
    assert isinstance(dataset.to_pandas(), pd.DataFrame)
    assert len(dataset) == len(records)
    for record, expected in zip(dataset, records):
        expected.metrics = record.metrics
        assert record == expected

    # log dataset
    api.log(dataset_class(records), name=dataset_names[2])
    dataset = api.load(dataset_names[2])
    assert len(dataset) == len(records)
    for record, expected in zip(dataset, records):
        record.metrics = expected.metrics
        assert record == expected


def test_passing_wrong_iterable_data(mocked_client):
    dataset_name = "test_log_single_records"
    mocked_client.delete(f"/api/datasets/{dataset_name}")
    with pytest.raises(Exception, match="Unknown record type"):
        api.log({"a": "010", "b": 100}, name=dataset_name)


def test_log_with_generator(mocked_client, monkeypatch):
    dataset_name = "test_log_with_generator"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    def generator(items: int = 10) -> Iterable[rg.TextClassificationRecord]:
        for i in range(0, items):
            yield rg.TextClassificationRecord(id=i, inputs={"text": "The text data"})

    api.log(generator(), name=dataset_name)


def test_create_ds_with_wrong_name(mocked_client):
    dataset_name = "Test Create_ds_with_wrong_name"

    with pytest.raises(InputValueError):
        api.log(
            rg.TextClassificationRecord(
                inputs={"text": "The text data"},
            ),
            name=dataset_name,
        )


def test_delete_dataset(mocked_client):
    dataset_name = "test_delete_dataset"
    mocked_client.delete(f"/api/datasets/{dataset_name}")

    api.log(
        rg.TextClassificationRecord(
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
    dataset_copy = "test_dataset_copy_new"
    other_workspace = "test_dataset_copy_ws"

    mocked_client.delete(f"/api/datasets/{dataset_copy}?workspace={other_workspace}")
    mocked_client.delete(f"/api/datasets/{dataset_copy}")
    mocked_client.delete(f"/api/datasets/{dataset}")

    record = rg.TextClassificationRecord(
        id=0,
        text="This is the record input",
        annotation_agent="test",
        annotation=["T"],
    )
    api.log(record, name=dataset)

    api.copy(dataset, name_of_copy=dataset_copy)
    ds, ds_copy = api.load(name=dataset), api.load(name=dataset_copy)
    df, df_copy = ds.to_pandas(), ds_copy.to_pandas()

    assert df.equals(df_copy)

    api.log(record, name=dataset_copy)

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
        mocked_client.add_workspaces_to_argilla_user([new_workspace])

        mocked_client.delete(f"/api/datasets/{dataset}")
        mocked_client.delete(f"/api/datasets/{dataset_copy}")
        mocked_client.delete(f"/api/datasets/{dataset_copy}?workspace={new_workspace}")

        api.log(
            rg.TextClassificationRecord(
                id=0,
                text="This is the record input",
                annotation_agent="test",
                annotation=["T"],
            ),
            name=dataset,
        )
        ds = api.load(dataset)
        df = ds.to_pandas()
        api.copy(dataset, name_of_copy=dataset_copy, workspace=new_workspace)
        api.set_workspace(new_workspace)
        df_copy = api.load(dataset_copy).to_pandas()
        assert df.equals(df_copy)

        with pytest.raises(AlreadyExistsApiError):
            api.copy(dataset_copy, name_of_copy=dataset_copy, workspace=new_workspace)
    finally:
        mocked_client.reset_argilla_workspaces()
        api.init()  # reset workspace


def test_update_record(mocked_client):
    dataset = "test_update_record"
    mocked_client.delete(f"/api/datasets/{dataset}")

    expected_inputs = ["This is a text"]
    record = rg.TextClassificationRecord(
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
    df = df.to_pandas()
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["annotation"] == "T"
    # This record will replace the old one
    record = rg.TextClassificationRecord(
        id=0,
        inputs=expected_inputs,
    )

    api.log(
        record,
        name=dataset,
    )

    df = api.load(name=dataset)
    df = df.to_pandas()
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["annotation"] is None
    assert records[0]["annotation_agent"] is None


def test_text_classifier_with_inputs_list(mocked_client):
    dataset = "test_text_classifier_with_inputs_list"
    mocked_client.delete(f"/api/datasets/{dataset}")

    expected_inputs = ["A", "List", "of", "values"]
    api.log(
        rg.TextClassificationRecord(
            id=0,
            inputs=expected_inputs,
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset,
    )

    df = api.load(name=dataset)
    df = df.to_pandas()
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["inputs"]["text"] == expected_inputs


def test_load_with_ids_list(mocked_client, supported_vector_search):
    dataset = "test_load_with_ids_list"
    mocked_client.delete(f"/api/datasets/{dataset}")

    expected_data = 100
    create_some_data_for_text_classification(
        mocked_client,
        dataset,
        n=expected_data,
        with_vectors=supported_vector_search,
    )
    ds = api.load(name=dataset, ids=[3, 5])
    assert len(ds) == 2


def test_load_with_query(mocked_client, supported_vector_search):
    dataset = "test_load_with_query"
    mocked_client.delete(f"/api/datasets/{dataset}")
    sleep(1)

    expected_data = 4
    create_some_data_for_text_classification(
        mocked_client,
        dataset,
        n=expected_data,
        with_vectors=supported_vector_search,
    )
    ds = api.load(name=dataset, query="id:1")
    ds = ds.to_pandas()
    assert len(ds) == 1
    assert ds.id.iloc[0] == 1


def test_load_as_pandas(mocked_client, supported_vector_search):
    dataset = "test_load_as_pandas"
    mocked_client.delete(f"/api/datasets/{dataset}")
    sleep(1)

    expected_data = 4
    server_vectors_cfg = create_some_data_for_text_classification(
        mocked_client,
        dataset,
        n=expected_data,
        with_vectors=supported_vector_search,
    )

    records = api.load(name=dataset)
    assert isinstance(records, rg.DatasetForTextClassification)
    assert isinstance(records[0], rg.TextClassificationRecord)

    if supported_vector_search:
        for record in records:
            for vector in record.vectors:
                assert server_vectors_cfg[vector]["value"] == record.vectors[vector]


@pytest.mark.parametrize(
    "span,valid",
    [
        ((1, 2), False),
        ((0, 4), True),
        ((0, 5), True),  # automatic correction
    ],
)
def test_token_classification_spans(span, valid):
    texto = "Esto es una prueba"
    if valid:
        rg.TokenClassificationRecord(
            text=texto,
            tokens=texto.split(),
            prediction=[("test", *span)],
        )
    else:
        with pytest.raises(
            ValueError,
            match="Following entity spans are not aligned with provided tokenization\n"
            r"Spans:\n\('test', 1, 2\) - 's'\n"
            r"Tokens:\n\['Esto', 'es', 'una', 'prueba'\]",
        ):
            rg.TokenClassificationRecord(
                text=texto,
                tokens=texto.split(),
                prediction=[("test", *span)],
            )


def test_load_text2text(mocked_client, supported_vector_search):
    vectors = {"bert_uncased": [1.2, 3.4, 6.4, 6.4]}

    records = []
    for i in range(0, 2):
        record = rg.Text2TextRecord(
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
        if supported_vector_search:
            record.vectors = vectors
        records.append(record)

    dataset = "test_load_text2text"
    api.delete(dataset)
    api.log(records, name=dataset)

    df = api.load(name=dataset)
    assert len(df) == 2
    if supported_vector_search:
        for record in df:
            assert record.vectors["bert_uncased"] == vectors["bert_uncased"]


def test_client_workspace(mocked_client):
    api = Argilla()
    ws = api.get_workspace()
    assert ws == "argilla"

    for ws in [None, ""]:
        with pytest.raises(Exception, match="Must provide a workspace"):
            api.set_workspace(ws)

    # Mocking user
    api.user.workspaces = ["a", "b"]

    with pytest.raises(Exception, match="Wrong provided workspace c"):
        api.set_workspace("c")

    api.set_workspace("argilla")
    assert api.get_workspace() == "argilla"


def test_load_sort(mocked_client):
    records = [
        rg.TextClassificationRecord(
            text="test text",
            id=i,
        )
        for i in ["1str", 1, 2, 11, "2str", "11str"]
    ]

    dataset = "test_load_sort"
    api.delete(dataset)
    api.log(records, name=dataset)

    # check sorting policies
    ds = api.load(name=dataset)
    print(ds)
    df = ds.to_pandas()
    print(df.head())
    assert list(df.id) == [1, 11, "11str", "1str", 2, "2str"]
    ds = api.load(name=dataset, ids=[1, 2, 11])
    df = ds.to_pandas()
    assert list(df.id) == [1, 2, 11]
    ds = api.load(name=dataset, ids=["1str", "2str", "11str"])
    df = ds.to_pandas()
    assert list(df.id) == ["11str", "1str", "2str"]
