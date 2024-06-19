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
import re
import warnings
from pathlib import Path
from time import sleep
from typing import Iterable
from uuid import uuid4

import datasets
import httpx
import pandas as pd
import pytest
from argilla_server.apis.v0.models.text_classification import (
    TextClassificationBulkRequest,
    TextClassificationRecordInputs,
)
from argilla_server.commons.models import TaskStatus
from argilla_server.models import User, UserRole
from argilla_v1._constants import (
    DEFAULT_API_KEY,
    WORKSPACE_HEADER_NAME,
)
from argilla_v1.client.api import (
    delete,
    delete_records,
    get_workspace,
    list_datasets,
    load,
    log,
    set_workspace,
)
from argilla_v1.client.apis.status import ApiInfo, Status
from argilla_v1.client.client import Argilla
from argilla_v1.client.datasets import (
    DatasetForText2Text,
    DatasetForTextClassification,
    DatasetForTokenClassification,
)
from argilla_v1.client.enums import DatasetType
from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla_v1.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla_v1.client.feedback.schemas.fields import TextField
from argilla_v1.client.feedback.schemas.questions import TextQuestion
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.models import (
    Text2TextRecord,
    TextClassificationRecord,
    TokenClassificationRecord,
)
from argilla_v1.client.sdk.client import AuthenticatedClient
from argilla_v1.client.sdk.commons.api import Response
from argilla_v1.client.sdk.commons.errors import (
    AlreadyExistsApiError,
    ForbiddenApiError,
    GenericApiError,
    HttpResponseError,
    InputValueError,
    NotFoundApiError,
    UnauthorizedApiError,
    ValidationApiError,
)
from argilla_v1.client.sdk.datasets.models import Dataset, TaskType
from argilla_v1.client.sdk.users import api as users_api
from argilla_v1.client.sdk.users.models import UserModel
from argilla_v1.client.sdk.v1.workspaces import api as workspaces_api_v1
from argilla_v1.client.sdk.workspaces.models import WorkspaceModel
from argilla_v1.client.singleton import active_client, init
from httpx import ConnectError

from tests.factories import UserFactory, WorkspaceFactory
from tests.integration.utils import delete_ignoring_errors


def create_some_data_for_text_classification(client: AuthenticatedClient, name: str, n: int, with_vectors: bool = True):
    n = n or 10

    records = [
        TextClassificationRecordInputs(**data)
        for idx in range(0, n, 2)
        for data in [
            {
                "id": idx,
                "inputs": {"data": "my data"},
                "multi_label": True,
                "metadata": {"field_one": "value one", "field_two": "value 2"},
                "status": TaskStatus.validated,
                "annotation": {"agent": "test", "labels": [{"class": "Test"}, {"class": "Mocking"}]},
            },
            {
                "id": idx + 1,
                "inputs": {"data": "my data"},
                "multi_label": True,
                "metadata": {"field_one": "another value one", "field_two": "value 2"},
                "status": TaskStatus.validated,
                "prediction": {"agent": "test", "labels": [{"class": "NoClass"}]},
                "annotation": {"agent": "test", "labels": [{"class": "Test"}]},
            },
        ]
    ]
    vectors = [
        {"bert_cased": {"record_properties": ["data"], "value": [1.2, 2.3, 3.4, 4.5]}},
        {"bert_cased": {"record_properties": ["data"], "value": [1.2, 2.3, 3.4, 4.5]}},
    ] * n

    if with_vectors:
        for record, record_vectors in zip(records, vectors):
            record.vectors = record_vectors

    client.post(
        "/api/datasets", json={"name": name, "task": TaskType.text_classification.value, "workspace": "argilla"}
    )

    client.post(
        f"/api/datasets/{name}/{TaskType.text_classification.value}:bulk",
        json=TextClassificationBulkRequest(
            tags={"env": "test", "class": "text classification"},
            metadata={"config": {"the": "config"}},
            records=records,
        ).dict(by_alias=True),
    )

    data = {}
    for vector_cfg in vectors:
        data.update(vector_cfg)

    return data


@pytest.fixture
def mock_init_ok(monkeypatch):
    """Creating of mock_get method from the class, and monkeypatch application.

    It will return a 200 status code, emulating the correct login.
    """
    from argilla_v1 import __version__ as rg_version

    def mock_get_info(*args, **kwargs):
        return ApiInfo(version=rg_version)

    def mock_whoami(*args, **kwargs) -> Response:
        return UserModel(
            id=uuid4(),
            username="mock_username",
            first_name="mock_first_name",
            role="admin",
            api_key="mock_api_key",
            workspaces=["mock_workspace"],
            inserted_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )

    def mock_list_workspaces(*args, **kwargs):
        return Response(
            content=b"",
            parsed=[
                WorkspaceModel(
                    id=uuid4(),
                    name="mock_workspace",
                    inserted_at=datetime.datetime.utcnow(),
                    updated_at=datetime.datetime.utcnow(),
                )
            ],
            status_code=200,
            headers={},
        )

    monkeypatch.setattr(Status, "get_info", mock_get_info)
    monkeypatch.setattr(users_api, "whoami", mock_whoami)
    monkeypatch.setattr(workspaces_api_v1, "list_workspaces_me", mock_list_workspaces)


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
            return UserModel(
                id=uuid4(),
                username="mock_username",
                first_name="mock_first_name",
                role="admin",
                api_key="mock_api_key",
                workspaces=["mock_workspace"],
                inserted_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
            )

    monkeypatch.setattr(users_api, "whoami", mock_get)


def test_init_uppercase_workspace(argilla_user: User):
    with pytest.raises(InputValueError):
        init(workspace="UPPERCASE_WORKSPACE")


@pytest.mark.skip(reason="Mock response is not working")
def test_init_correct(mock_init_ok):
    """Testing correct default initialization

    It checks if the _client created is a argillaClient object.
    """

    client = active_client()

    assert active_client().http_client == AuthenticatedClient(
        base_url="http://localhost:6900",
        token=DEFAULT_API_KEY,
        timeout=60.0,
        headers={WORKSPACE_HEADER_NAME: client.user.username},
    )

    url = "mock_url"
    api_key = "mock_api_key"
    workspace_name = client.user.workspaces[0]

    init(api_url=url, api_key=api_key, workspace=workspace_name, timeout=42)
    assert active_client().http_client == AuthenticatedClient(
        base_url=url,
        token=api_key,
        timeout=42,
        headers={WORKSPACE_HEADER_NAME: workspace_name},
    )


def test_init_environment_url(mock_init_ok, monkeypatch):
    """Testing initialization with api_url provided via environment variable

    It checks the url in the environment variable gets passed to client.
    """
    workspace_name = "mock_workspace"
    url = "http://mock_url"
    api_key = "mock_api_key"

    monkeypatch.setenv("ARGILLA_API_URL", url)
    monkeypatch.setenv("ARGILLA_API_KEY", api_key)
    monkeypatch.setenv("ARGILLA_WORKSPACE", workspace_name)

    init()
    assert active_client()._client == AuthenticatedClient(
        base_url=url,
        token=api_key,
        timeout=60,
        headers={WORKSPACE_HEADER_NAME: workspace_name},
    )


def test_init_with_stored_credentials(mock_init_ok, mocker):
    mocker.patch(
        "builtins.open",
        mocker.mock_open(
            read_data='{"api_url": "http://integration-test.com:6900", "api_key": "integration.test", "workspace": "mock_workspace", "extra_headers": {"X-Integration-Test": "true"}}'
        ),
    )
    path_mock = mocker.patch.object(Path, "exists")
    path_mock.return_value = True

    init()

    assert active_client()._client == AuthenticatedClient(
        base_url="http://integration-test.com:6900",
        token="integration.test",
        timeout=60,
        headers={WORKSPACE_HEADER_NAME: "mock_workspace", "X-Integration-Test": "true"},
    )


def test_init_with_stored_credentials_overriding_workspace(mock_init_ok, mocker):
    mocker.patch(
        "builtins.open",
        mocker.mock_open(
            read_data='{"api_url": "http://integration-test.com:6900", "api_key": "integration.test", "workspace": "my_workspace", "extra_headers": {"X-Integration-Test": "true"}}'
        ),
    )
    path_mock = mocker.patch.object(Path, "exists")
    path_mock.return_value = True

    init(workspace="mock_workspace")

    assert active_client()._client == AuthenticatedClient(
        base_url="http://integration-test.com:6900",
        token="integration.test",
        timeout=60,
        headers={WORKSPACE_HEADER_NAME: "mock_workspace", "X-Integration-Test": "true"},
    )


@pytest.mark.asyncio
async def test_init_with_workspace(owner: User) -> None:
    workspace = await WorkspaceFactory.create(name="test_workspace")

    init(api_key=owner.api_key, workspace=workspace.name)
    assert get_workspace() == workspace.name


def test_set_workspace_with_missing_workspace(owner: User) -> None:
    init(api_key=owner.api_key)
    with pytest.raises(ValueError):
        set_workspace("missing-workspace")


def test_init_with_missing_workspace(owner: User) -> None:
    with pytest.raises(ValueError):
        init(api_key=owner.api_key, workspace="missing-workspace")


def test_trailing_slash(mock_init_ok):
    """Testing initialization with provided api_url via environment variable and argument

    It checks the trailing slash is removed in all cases
    """
    init(api_url="http://mock.com/")
    assert active_client()._client.base_url == "http://mock.com"


def test_log_something(argilla_user: User):
    dataset_name = "test-dataset"

    api = Argilla(api_key=argilla_user.api_key, workspace=argilla_user.username)
    api.delete(dataset_name)

    response = api.log(name=dataset_name, records=TextClassificationRecord(inputs={"text": "This is a test"}))

    assert response.processed == 1
    assert response.failed == 0

    results = api.search.search_records(dataset_name, task=TaskType.text_classification)
    assert results.total == 1
    assert len(results.records) == 1
    assert results.records[0].inputs["text"] == "This is a test"


def test_load_feedback_dataset(argilla_user: User):
    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    dataset = FeedbackDataset(fields=[TextField(name="text-field")], questions=[TextQuestion(name="text-question")])

    dataset.add_records(
        FeedbackRecord(
            fields={"text-field": "unit-test"},
        )
    )

    dataset.push_to_argilla(name="unit-test", workspace=argilla_user.username)

    with pytest.warns(UserWarning):
        dataset = load(name="unit-test", workspace=argilla_user.username)

    assert isinstance(dataset, RemoteFeedbackDataset)


def test_load_empty_string(argilla_user: User):
    dataset_name = "test-dataset"

    api = Argilla(api_key=argilla_user.api_key, workspace=argilla_user.username)
    api.delete(dataset_name)

    api.log(name=dataset_name, records=TextClassificationRecord(inputs={"text": "This is a test"}))
    assert len(api.load(name=dataset_name, query="")) == 1
    assert len(api.load(name=dataset_name, query="  ")) == 1


def test_load_limits(argilla_user: User):
    dataset = "test_load_limits"

    api = Argilla(api_key=argilla_user.api_key)
    api.delete(dataset)

    create_some_data_for_text_classification(api.http_client, dataset, n=50)

    limit_data_to = 10
    ds = api.load(name=dataset, limit=limit_data_to)
    assert len(ds) == limit_data_to

    ds = api.load(name=dataset, limit=limit_data_to)
    assert len(ds) == limit_data_to


def test_log_records_with_too_long_text(api: Argilla):
    dataset_name = "test_log_records_with_too_long_text"
    api.delete(dataset_name)
    item = TextClassificationRecord(inputs={"text": "This is a toooooo long text\n" * 10000})

    api.log([item], name=dataset_name)


def test_not_found_response(api: Argilla):
    with pytest.raises(NotFoundApiError):
        api.load(name="not-found")


def test_log_without_name(argilla_user: User):
    with pytest.raises(
        InputValueError,
        match="Empty dataset name has been passed as argument.",
    ):
        log(
            TextClassificationRecord(inputs={"text": "This is a single record. Only this. No more."}),
            name=None,
        )


def test_log_passing_empty_records_list(argilla_user: User):
    with pytest.raises(
        InputValueError,
        match="Empty record list has been passed as argument.",
    ):
        log(records=[], name="ds")


def test_log_deprecated_chunk_size(argilla_user: User):
    dataset_name = "test_log_deprecated_chunk_size"
    delete_ignoring_errors(dataset_name)
    record = TextClassificationRecord(text="My text")
    with pytest.warns(FutureWarning, match="`chunk_size`.*`batch_size`"):
        log(records=[record], name=dataset_name, chunk_size=100)


def test_large_batch_size_warning(argilla_user: User):
    dataset_name = "test_large_batch_size_warning"
    delete_ignoring_errors(dataset_name)
    record = TextClassificationRecord(text="My text")

    with pytest.warns(UserWarning, match="batch size is noticeably large"):
        log(records=[record], name=dataset_name, batch_size=10000)


def test_log_background(argilla_user: User):
    """Verify that logs can be delayed via the background parameter."""
    dataset_name = "test_log_background"

    api = Argilla(api_key=argilla_user.api_key)
    api.delete(dataset_name)

    # Log in the background, and extract the future
    sample_text = "Sample text for testing"
    future = api.log(
        TextClassificationRecord(text=sample_text),
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


def test_log_background_with_error(monkeypatch, argilla_user: User):
    dataset_name = "test_log_background_with_error"
    delete_ignoring_errors(dataset_name)

    # Log in the background, and extract the future
    sample_text = "Sample text for testing"

    def raise_http_error(*args, **kwargs):
        raise httpx.ConnectError("Mock error", request=None)

    monkeypatch.setattr(active_client().http_client, "post", raise_http_error)

    future = log(TextClassificationRecord(text=sample_text), name=dataset_name, background=True)
    with pytest.raises(ConnectError):
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
def test_delete_with_errors(monkeypatch, argilla_user: User, status, error_type):
    def send_mock_response_with_http_status(status: int):
        def inner(*args, **kwargs):
            return httpx.Response(
                status_code=status,
                json={"detail": {"code": "error:code", "params": {"message": "Mock"}}},
            )

        return inner

    with pytest.raises(error_type):
        monkeypatch.setattr(httpx, "get", send_mock_response_with_http_status(status))
        delete("dataset")


@pytest.mark.parametrize(
    "records, dataset_class",
    [
        ("singlelabel_textclassification_records", DatasetForTextClassification),
        ("multilabel_textclassification_records", DatasetForTextClassification),
        ("tokenclassification_records", DatasetForTokenClassification),
        ("text2text_records", DatasetForText2Text),
    ],
)
def test_general_log_load(argilla_user: User, request, records, dataset_class):
    dataset_names = [
        f"test_general_log_load_{dataset_class.__name__.lower()}_" + input_type
        for input_type in ["single", "list", "dataset"]
    ]

    for name in dataset_names:
        delete_ignoring_errors(name)

    records = request.getfixturevalue(records)

    # log single records
    log(records[0], name=dataset_names[0])
    dataset = load(dataset_names[0])
    records[0].metrics = dataset[0].metrics
    assert dataset[0] == records[0]

    # log list of records
    log(records, name=dataset_names[1])
    dataset = load(dataset_names[1])
    # check if returned records can be converted to other formats
    assert isinstance(dataset.to_datasets(), datasets.Dataset)
    assert isinstance(dataset.to_pandas(), pd.DataFrame)
    assert len(dataset) == len(records)
    for record, expected in zip(dataset, records):
        expected.metrics = record.metrics
        assert record == expected

    # log dataset
    log(dataset_class(records), name=dataset_names[2])
    dataset = load(dataset_names[2])
    assert len(dataset) == len(records)
    for record, expected in zip(dataset, records):
        record.metrics = expected.metrics
        assert record == expected


@pytest.mark.parametrize(
    "records, dataset_class",
    [("singlelabel_textclassification_records", DatasetForTextClassification)],
)
def test_log_load_with_workspace(argilla_user: User, request, records, dataset_class):
    dataset_names = [
        f"test_general_log_load_{dataset_class.__name__.lower()}_" + input_type
        for input_type in ["single", "list", "dataset"]
    ]
    for name in dataset_names:
        delete_ignoring_errors(name)

    records = request.getfixturevalue(records)

    log(records, name=dataset_names[0], workspace="argilla")
    ds = load(dataset_names[0], workspace="argilla")
    delete_records(dataset_names[0], ids=[rec.id for rec in ds][:1], workspace="argilla")
    delete_ignoring_errors(dataset_names[0], workspace="argilla")


def test_passing_wrong_iterable_data(argilla_user: User):
    dataset_name = "test_log_single_records"
    delete_ignoring_errors(dataset_name)
    with pytest.raises(Exception, match="Unknown record type"):
        log({"a": "010", "b": 100}, name=dataset_name)


def test_log_with_generator(argilla_user: User):
    dataset_name = "test_log_with_generator"
    delete_ignoring_errors(dataset_name)

    def generator(items: int = 10) -> Iterable[TextClassificationRecord]:
        for i in range(0, items):
            yield TextClassificationRecord(id=i, inputs={"text": "The text data"})

    log(generator(), name=dataset_name)


def test_create_ds_with_wrong_name(argilla_user: User):
    dataset_name = "Test Create_ds_with_wrong_name"

    with pytest.raises(InputValueError):
        log(
            TextClassificationRecord(
                inputs={"text": "The text data"},
            ),
            name=dataset_name,
        )


def test_delete_dataset(argilla_user: User):
    dataset_name = "test_delete_dataset"
    delete_ignoring_errors(dataset_name)

    log(
        TextClassificationRecord(
            id=0,
            inputs={"text": "The text data"},
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset_name,
    )
    load(name=dataset_name)
    delete_ignoring_errors(name=dataset_name)
    sleep(1)
    with pytest.raises(NotFoundApiError):
        load(name=dataset_name)


def test_delete_feedback_dataset(argilla_user: User):
    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    dataset = FeedbackDataset(fields=[TextField(name="text-field")], questions=[TextQuestion(name="text-question")])

    dataset.add_records(
        FeedbackRecord(
            fields={"text-field": "unit-test"},
        )
    )

    dataset.push_to_argilla(name="unit-test", workspace=argilla_user.username)

    with pytest.warns(UserWarning):
        delete(name="unit-test", workspace=argilla_user.username)

    with pytest.raises(ValueError):
        FeedbackDataset.from_argilla(name="unit-test", workspace=argilla_user.username)


def test_log_with_wrong_name(argilla_user: User):
    with pytest.raises(InputValueError):
        log(name="Bad name", records=["whatever"])

    with pytest.raises(InputValueError):
        log(name="anotherWrongName", records=["whatever"])


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.asyncio
async def test_dataset_copy(role: UserRole):
    dataset_name = "test_dataset_copy"
    dataset_copy_name = "test_dataset_copy_new"

    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create(role=role, workspaces=[workspace])

    api = Argilla(api_key=user.api_key, workspace=workspace.name)

    api.delete(dataset_name, workspace=workspace.name)
    api.delete(dataset_copy_name, workspace=workspace.name)

    record = TextClassificationRecord(id=0, text="This is the record input", annotation_agent="test", annotation=["T"])
    api.log(record, name=dataset_name)
    api.copy(dataset_name, name_of_copy=dataset_copy_name)

    ds, ds_copy = api.load(name=dataset_name), api.load(name=dataset_copy_name)
    df, df_copy = ds.to_pandas(), ds_copy.to_pandas()

    assert df.equals(df_copy)

    api.log(record, name=dataset_copy_name)

    with pytest.raises(AlreadyExistsApiError):
        api.copy(dataset_name, name_of_copy=dataset_copy_name)
    with pytest.raises(NotFoundApiError, match="other-workspace"):
        api.copy(dataset_name, name_of_copy=dataset_copy_name, workspace="other-workspace")


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.asyncio
async def test_dataset_copy_to_another_workspace(role: UserRole):
    dataset_name = "test_dataset_copy_to_another_workspace"
    dataset_copy = "new_dataset"

    workspace = await WorkspaceFactory.create()
    workspace_02 = await WorkspaceFactory.create()
    user = await UserFactory.create(role=role, workspaces=[workspace, workspace_02])

    api = Argilla(api_key=user.api_key, workspace=workspace.name)

    api.delete(dataset_name, workspace=workspace.name)
    api.delete(dataset_copy, workspace=workspace.name)
    api.delete(dataset_name, workspace=workspace_02.name)
    api.delete(dataset_copy, workspace=workspace_02.name)

    api.log(
        TextClassificationRecord(id=0, text="This is the record input", annotation_agent="test", annotation=["T"]),
        name=dataset_name,
    )
    ds = api.load(dataset_name)
    df = ds.to_pandas()

    api.copy(dataset_name, name_of_copy=dataset_copy, workspace=workspace_02.name)

    api.set_workspace(workspace_02.name)
    df_copy = api.load(dataset_copy).to_pandas()
    assert df.equals(df_copy)
    with pytest.raises(AlreadyExistsApiError):
        api.copy(dataset_copy, name_of_copy=dataset_copy, workspace=workspace_02.name)


def test_update_record(argilla_user: User):
    dataset = "test_update_record"
    delete_ignoring_errors(dataset)

    expected_inputs = ["This is a text"]
    record = TextClassificationRecord(id=0, inputs=expected_inputs, annotation_agent="test", annotation=["T"])
    log(record, name=dataset)

    df = load(name=dataset)
    df = df.to_pandas()
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["annotation"] == "T"
    # This record will be partially updated
    record = TextClassificationRecord(id=0, inputs=expected_inputs, metadata={"a": "value"})

    log(record, name=dataset)

    df = load(name=dataset)
    df = df.to_pandas()
    records = df.to_dict(orient="records")

    assert len(records) == 1
    assert records[0]["annotation"] == "T"
    assert records[0]["annotation_agent"] == "test"
    assert records[0]["metadata"] == {"a": "value"}


def test_text_classifier_with_inputs_list(argilla_user: User):
    dataset = "test_text_classifier_with_inputs_list"

    delete_ignoring_errors(dataset)

    expected_inputs = ["A", "List", "of", "values"]
    log(
        TextClassificationRecord(
            id=0,
            inputs=expected_inputs,
            annotation_agent="test",
            annotation=["T"],
        ),
        name=dataset,
    )

    df = load(name=dataset)
    df = df.to_pandas()
    records = df.to_dict(orient="records")
    assert len(records) == 1
    assert records[0]["inputs"]["text"] == expected_inputs


def test_load_with_ids_list(api: Argilla):
    dataset = "test_load_with_ids_list"
    api.delete(name=dataset)

    expected_data = 100
    create_some_data_for_text_classification(api.client, dataset, n=expected_data)
    ds = api.load(name=dataset, ids=[3, 5])
    assert len(ds) == 2


def test_load_with_query(api: Argilla):
    dataset = "test_load_with_query"
    api.delete(dataset)
    sleep(1)

    expected_data = 4
    create_some_data_for_text_classification(
        api.client,
        dataset,
        n=expected_data,
    )
    ds = api.load(name=dataset, query="id:1")
    ds = ds.to_pandas()
    assert len(ds) == 1
    assert ds.id.iloc[0] == 1


def test_load_with_sort(api: Argilla):
    dataset = "test_load_with_sort"
    api.delete(dataset)
    sleep(1)

    expected_data = 4
    api.log([TextClassificationRecord(text=text) for text in ["This is my text"] * expected_data], name=dataset)
    with pytest.raises(
        ValueError, match=re.escape("sort must be a dict formatted as List[Tuple[<field_name>, 'asc|desc']]")
    ):
        api.load(name=dataset, sort=[("event_timestamp", "ascc")])

    ds = api.load(name=dataset, sort=[("event_timestamp", "asc")])
    assert all([(ds[idx].event_timestamp <= ds[idx + 1].event_timestamp) for idx in range(len(ds) - 1)])

    ds = api.load(name=dataset, sort=[("event_timestamp", "desc")])
    assert all([(ds[idx].event_timestamp >= ds[idx + 1].event_timestamp) for idx in range(len(ds) - 1)])


def test_load_as_pandas(api: Argilla):
    dataset = "test_load_as_pandas"
    api.delete(dataset)
    sleep(1)

    expected_data = 4
    server_vectors_cfg = create_some_data_for_text_classification(
        api.client,
        dataset,
        n=expected_data,
    )

    records = api.load(name=dataset)
    assert isinstance(records, DatasetForTextClassification)
    assert isinstance(records[0], TextClassificationRecord)

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
        TokenClassificationRecord(
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
            TokenClassificationRecord(
                text=texto,
                tokens=texto.split(),
                prediction=[("test", *span)],
            )


def test_load_text2text(api: Argilla):
    vectors = {"bert_uncased": [1.2, 3.4, 6.4, 6.4]}

    records = []
    for i in range(0, 2):
        record = Text2TextRecord(
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
        record.vectors = vectors
        records.append(record)

    dataset = "test_load_text2text"
    api.delete(dataset)
    api.log(records, name=dataset)

    df = api.load(name=dataset)
    assert len(df) == 2
    for record in df:
        assert record.vectors["bert_uncased"] == vectors["bert_uncased"]


def test_client_workspace(api: Argilla, argilla_user: User):
    workspace = api.get_workspace()
    assert workspace == argilla_user.username

    with pytest.raises(Exception, match="Must provide a workspace"):
        api.set_workspace(None)

    with pytest.raises(Exception, match="Wrong provided workspace 'not-found'"):
        api.set_workspace("not-found")

    api.set_workspace(argilla_user.username)
    assert api.get_workspace() == argilla_user.username


def test_load_sort(api: Argilla):
    records = [TextClassificationRecord(text="test text", id=i) for i in ["1str", 1, 2, 11, "2str", "11str"]]

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
    assert list(df.id) == [1, 11, 2]
    ds = api.load(name=dataset, ids=["1str", "2str", "11str"])
    df = ds.to_pandas()
    assert list(df.id) == ["11str", "1str", "2str"]


def test_not_aligned_argilla_versions(monkeypatch):
    from argilla_v1 import __version__ as rg_version

    def mock_get_info(*args, **kwargs):
        return ApiInfo(version="1.0.0")

    def mock_whoami(*args, **kwargs) -> Response:
        return UserModel(
            id=uuid4(),
            username="mock_username",
            first_name="mock_first_name",
            role="admin",
            api_key="mock_api_key",
            workspaces=["mock_workspace"],
            inserted_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )

    monkeypatch.setattr(Status, "get_info", mock_get_info)
    monkeypatch.setattr(users_api, "whoami", mock_whoami)

    with pytest.warns(
        UserWarning,
        match=rf"You're connecting to Argilla Server 1.0.0 using a different client version \({rg_version}\)",
    ):
        Argilla()


@pytest.mark.skip
def test_list_datasets(argilla_user: User):
    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    log(
        TextClassificationRecord(id=0, inputs={"text": "The text data"}, annotation_agent="test", annotation=["T"]),
        name="unit-test-dataset",
    )

    dataset = FeedbackDataset(fields=[TextField(name="text-field")], questions=[TextQuestion(name="text-question")])

    dataset.add_records(
        FeedbackRecord(
            fields={"text-field": "unit-test"},
        )
    )

    dataset.push_to_argilla(name="unit-test", workspace=argilla_user.username)

    datasets = list_datasets()

    assert len(datasets) == 2


@pytest.mark.skip
def test_list_datasets_only_other_datasets(argilla_user: User):
    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    log(
        TextClassificationRecord(id=0, inputs={"text": "The text data"}, annotation_agent="test", annotation=["T"]),
        name="unit-test-dataset",
    )

    dataset = FeedbackDataset(fields=[TextField(name="text-field")], questions=[TextQuestion(name="text-question")])

    dataset.add_records(
        FeedbackRecord(
            fields={"text-field": "unit-test"},
        )
    )

    dataset.push_to_argilla(name="unit-test", workspace=argilla_user.username)

    datasets = list_datasets(type=DatasetType.other)

    assert len(datasets) == 1
    assert isinstance(datasets[0], Dataset)


def test_list_datasets_only_feedback_datasets(argilla_user: User):
    init(api_key=argilla_user.api_key, workspace=argilla_user.username)

    log(
        TextClassificationRecord(id=0, inputs={"text": "The text data"}, annotation_agent="test", annotation=["T"]),
        name="unit-test-dataset",
    )

    dataset = FeedbackDataset(fields=[TextField(name="text-field")], questions=[TextQuestion(name="text-question")])

    dataset.add_records(
        FeedbackRecord(
            fields={"text-field": "unit-test"},
        )
    )

    dataset.push_to_argilla(name="unit-test", workspace=argilla_user.username)

    datasets = list_datasets(type=DatasetType.feedback)

    assert len(datasets) == 1
    assert isinstance(datasets[0], RemoteFeedbackDataset)


def test_aligned_argilla_versions(mock_init_ok):
    with warnings.catch_warnings(record=True) as record:
        Argilla()
        for warning in record:
            assert "You're connecting to Argilla Server" not in str(warning.message)
