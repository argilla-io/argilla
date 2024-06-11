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
import asyncio
import contextlib
import tempfile
import uuid
from typing import TYPE_CHECKING, AsyncGenerator, Dict, Generator

import httpx
import pytest
import pytest_asyncio
from argilla_server import telemetry as server_telemetry
from argilla_server.cli.database.migrate import migrate_db
from argilla_server.database import get_async_db
from argilla_server.models import User, UserRole, Workspace
from argilla_server.settings import settings
from argilla_v1._constants import API_KEY_HEADER_NAME, DEFAULT_API_KEY
from argilla_v1.client.api import log
from argilla_v1.client.apis.datasets import TextClassificationSettings
from argilla_v1.client.client import Argilla, AuthenticatedClient
from argilla_v1.client.datasets import read_datasets
from argilla_v1.client.models import Text2TextRecord, TextClassificationRecord
from argilla_v1.client.sdk.users import api as users_api
from argilla_v1.client.singleton import ArgillaSingleton
from argilla_v1.datasets import configure_dataset
from argilla_v1.utils import telemetry as client_telemetry
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from tests.factories import (
    AnnotatorFactory,
    OwnerFactory,
    UserFactory,
    WorkspaceFactory,
)
from tests.integration.utils import delete_ignoring_errors
from tests.pydantic_v1 import BaseModel

from ..database import SyncTestSession, TestSession, set_task
from .helpers import SecuredClient

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture
    from sqlalchemy import Connection
    from sqlalchemy.ext.asyncio import AsyncConnection
    from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def event_loop() -> Generator["asyncio.AbstractEventLoop", None, None]:
    loop = asyncio.get_event_loop_policy().get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def database_url_for_tests() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        settings.database_url = f"sqlite+aiosqlite:///{tmpdir}/test.db?check_same_thread=False"
        yield settings.database_url


@pytest_asyncio.fixture(scope="session")
async def connection(database_url_for_tests: str) -> AsyncGenerator["AsyncConnection", None]:
    set_task(asyncio.current_task())
    # Create a temp directory to store a SQLite database used for testing

    engine = create_async_engine(database_url_for_tests)
    conn = await engine.connect()
    TestSession.configure(bind=conn)
    migrate_db("head")

    yield conn

    migrate_db("base")
    await conn.close()
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def db(connection: "AsyncConnection") -> AsyncGenerator["AsyncSession", None]:
    await connection.begin_nested()
    session = TestSession()

    yield session

    await session.close()
    await TestSession.remove()
    await connection.rollback()


@pytest.fixture
def sync_connection(database_url_for_tests: str) -> Generator["Connection", None, None]:
    engine = create_engine(database_url_for_tests)
    conn = engine.connect()
    SyncTestSession.configure(bind=conn)
    migrate_db("head")

    yield conn

    migrate_db("base")
    conn.close()
    engine.dispose()


@pytest.fixture
def sync_db(sync_connection: "Connection") -> Generator["Session", None, None]:
    session = SyncTestSession()

    yield session

    session.close()
    SyncTestSession.remove()
    sync_connection.rollback()


@pytest.fixture(scope="function")
def client(request, mocker: "MockerFixture") -> Generator[TestClient, None, None]:
    from argilla_server import app
    from argilla_server.apis.routes import api_v0, api_v1

    async def override_get_async_db():
        session = TestSession()
        yield session

    mocker.patch("argilla_server._app._get_db_wrapper", wraps=contextlib.asynccontextmanager(override_get_async_db))
    # Here, we need to override the dependency for both versions of the API. This behavior changed from pull request #28
    # https://github.com/argilla-io/argilla-server/pull/28/files#diff-0cae8a7ee2d37098b1ad84b543d17cfc1e8535eed5fd6abac88c668bfe354cbbR98
    for api_app in [api_v0, api_v1]:
        api_app.dependency_overrides[get_async_db] = override_get_async_db

    raise_server_exceptions = request.param if hasattr(request, "param") else False
    with TestClient(app, raise_server_exceptions=raise_server_exceptions) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def elasticsearch_config():
    return {"hosts": settings.elasticsearch}


@pytest_asyncio.fixture(scope="function")
async def owner() -> User:
    return await OwnerFactory.create(first_name="Owner", username="owner", api_key="owner.apikey")


@pytest_asyncio.fixture(scope="function")
async def annotator() -> User:
    return await AnnotatorFactory.create(first_name="Annotator", username="annotator", api_key="annotator.apikey")


@pytest_asyncio.fixture(scope="function")
async def mock_user() -> User:
    workspace_a = await WorkspaceFactory.create(name="workspace-a")
    workspace_b = await WorkspaceFactory.create(name="workspace-b")
    return await UserFactory.create(
        first_name="Mock",
        username="mock-user",
        password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
        api_key="mock-user.apikey",
        workspaces=[workspace_a, workspace_b],
    )


@pytest.fixture(scope="function")
def owner_auth_header(owner: User) -> Dict[str, str]:
    return {API_KEY_HEADER_NAME: owner.api_key}


@pytest_asyncio.fixture(scope="function")
async def argilla_user() -> Generator[User, None, None]:
    user = await UserFactory.create(
        first_name="Argilla",
        username="argilla",
        role=UserRole.owner,
        password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
        api_key=DEFAULT_API_KEY,
        workspaces=[Workspace(name="argilla")],
    )
    yield user
    ArgillaSingleton.clear()


@pytest.fixture(scope="function")
def argilla_auth_header(argilla_user: User) -> Dict[str, str]:
    return {API_KEY_HEADER_NAME: argilla_user.api_key}


@pytest.fixture(autouse=True)
def server_telemetry_client(mocker: "MockerFixture") -> "MagicMock":
    mock_telemetry = mocker.Mock(server_telemetry.TelemetryClient)
    mock_telemetry.server_id = uuid.uuid4()

    server_telemetry._CLIENT = mock_telemetry
    return server_telemetry._CLIENT


@pytest.fixture(autouse=True)
def client_telemetry_client(mocker: "MockerFixture") -> "MagicMock":
    mock_telemetry = mocker.Mock(client_telemetry.TelemetryClient)
    mock_telemetry.machine_id = uuid.uuid4()

    client_telemetry._CLIENT = mock_telemetry
    return client_telemetry._CLIENT


@pytest.mark.parametrize("client", [True], indirect=True)
@pytest.fixture(autouse=True)
def using_test_client_from_argilla_python_client(
    monkeypatch, server_telemetry_client, client_telemetry_client, client: "TestClient"
):
    real_whoami = users_api.whoami

    def whoami_mocked(*args, **kwargs):
        client_arg = args[-1] if args else kwargs["client"]

        monkeypatch.setattr(client_arg, "__httpx__", client)
        client.headers.update(client_arg.get_headers())

        return real_whoami(client_arg)

    monkeypatch.setattr(users_api, "whoami", whoami_mocked)

    monkeypatch.setattr(httpx, "post", client.post)
    monkeypatch.setattr(httpx, "patch", client.patch)
    monkeypatch.setattr(httpx, "get", client.get)
    monkeypatch.setattr(httpx, "delete", client.delete)
    monkeypatch.setattr(httpx, "put", client.put)
    monkeypatch.setattr(httpx, "stream", client.stream)


@pytest.fixture
def api(argilla_user: User) -> Argilla:
    return Argilla(api_key=argilla_user.api_key, workspace=argilla_user.username)


@pytest.fixture
def mocked_client(
    monkeypatch, using_test_client_from_argilla_python_client, argilla_user: User, client: "TestClient"
) -> SecuredClient:
    client_ = SecuredClient(client, argilla_user)

    real_whoami = users_api.whoami

    def whoami_mocked(client: AuthenticatedClient):
        monkeypatch.setattr(client, "__httpx__", client_)
        return real_whoami(client)

    monkeypatch.setattr(users_api, "whoami", whoami_mocked)

    monkeypatch.setattr(httpx, "post", client_.post)
    monkeypatch.setattr(httpx, "patch", client_.patch)
    monkeypatch.setattr(httpx, "get", client_.get)
    monkeypatch.setattr(httpx, "delete", client_.delete)
    monkeypatch.setattr(httpx, "put", client_.put)

    from argilla_v1.client.singleton import active_api

    rb_api = active_api()
    monkeypatch.setattr(rb_api.http_client, "__httpx__", client_)

    return client_


@pytest.fixture
def dataset_token_classification(mocked_client: SecuredClient) -> str:
    from datasets import load_dataset

    dataset = "gutenberg_spacy_ner"

    dataset_ds = load_dataset(
        "argilla/gutenberg_spacy-ner",
        split="train[:3]",
        # This revision does not includes the vectors info, so tests will pass
        revision="fff5f572e4cc3127f196f46ba3f9914c6fd0d763",
    )

    dataset_rb = read_datasets(dataset_ds, task="TokenClassification")
    # Set annotations, required for training tests
    for rec in dataset_rb:
        # Strip off "score"
        rec.annotation = [prediction[:3] for prediction in rec.prediction]
        rec.annotation_agent = rec.prediction_agent
        rec.prediction = []
        rec.prediction_agent = None

    delete_ignoring_errors(dataset)
    log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture
def dataset_text_classification(mocked_client: SecuredClient) -> str:
    from datasets import load_dataset

    dataset = "banking_sentiment_setfit"

    dataset_ds = load_dataset(
        f"argilla/{dataset}",
        split="train[:3]",
    )
    dataset_rb = [TextClassificationRecord(text=rec["text"], annotation=rec["label"]) for rec in dataset_ds]
    labels = set([rec.annotation for rec in dataset_rb])
    configure_dataset(dataset, settings=TextClassificationSettings(label_schema=labels))

    delete_ignoring_errors(dataset)
    log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture
def dataset_text_classification_multi_label(mocked_client: SecuredClient) -> str:
    from datasets import load_dataset

    dataset = "research_titles_multi_label"

    dataset_ds = load_dataset("argilla/research_titles_multi-label", split="train[:50]")

    dataset_rb = read_datasets(dataset_ds, task="TextClassification")

    dataset_rb = [rec for rec in dataset_rb if rec.annotation]

    delete_ignoring_errors(dataset)
    log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture
def dataset_text2text(mocked_client: SecuredClient) -> str:
    from datasets import load_dataset

    dataset = "news_summary"

    dataset_ds = load_dataset("argilla/news-summary", split="train[:3]")

    records = []
    for entry in dataset_ds:
        records.append(Text2TextRecord(text=entry["text"], annotation=entry["prediction"][0]["text"]))

    delete_ignoring_errors(dataset)
    log(name=dataset, records=records)

    return dataset


class _MockResponse(BaseModel):
    id: str = "1234"


@pytest.fixture
def mocked_openai(mocker):
    # Mock the requests to OpenAI APIs
    response = _MockResponse()
    mocker.patch("openai.FineTune.retrieve", return_value=response)
    mocker.patch("openai.FineTuningJob.retrieve", return_value=response)
    mocker.patch("openai.Model.retrieve", return_value=response)
    mocker.patch("openai.FineTuningJob.create", return_value=response)
    mocker.patch("openai.FineTune.create", return_value=response)
    mocker.patch("openai.File.create", return_value=response)


@pytest.fixture
def mocked_trainer_push_to_huggingface(mocker: "MockerFixture"):
    # Mock the push_to_huggingface methods for the different trainers,
    # most of the functionality is already tested by the frameworks itself.
    # For transformers' model and tokenizer
    mocker.patch("transformers.PreTrainedModel.push_to_hub", return_value="model_url")
    mocker.patch("transformers.PreTrainedTokenizer.push_to_hub", return_value="model_url")
    # For setfit
    mocker.patch("setfit.trainer.SetFitTrainer.push_to_hub", return_value="model_url")
    # For peft
    mocker.patch("peft.PeftModel.push_to_hub", return_value="model_url")
    mocker.patch("transformers.PreTrainedTokenizerBase.push_to_hub", return_value="model_url")
    # For spacy and spacy-transformers
    mocker.patch("spacy_huggingface_hub.push", return_value={"url": "model_url"})
    # For trl
    mocker.patch("trl.trainer.sft_trainer.SFTTrainer.push_to_hub", return_value="model_url")
    mocker.patch("trl.trainer.reward_trainer.RewardTrainer.push_to_hub", return_value="model_url")
    mocker.patch("trl.trainer.base.BaseTrainer.push_to_hub", return_value="model_url")
    mocker.patch("trl.trainer.dpo_trainer.DPOTrainer.push_to_hub", return_value="model_url")
