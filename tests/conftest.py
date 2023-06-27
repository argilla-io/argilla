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

import tempfile
from typing import TYPE_CHECKING, Dict, Generator

import argilla as rg
import httpx
import pytest
from argilla._constants import API_KEY_HEADER_NAME, DEFAULT_API_KEY
from argilla.client.api import ArgillaSingleton, delete, log
from argilla.client.apis.datasets import TextClassificationSettings
from argilla.client.client import Argilla, AuthenticatedClient
from argilla.client.datasets import read_datasets
from argilla.client.models import Text2TextRecord, TextClassificationRecord
from argilla.client.sdk.users import api as users_api
from argilla.datasets.__init__ import configure_dataset
from argilla.server.commons import telemetry
from argilla.server.commons.telemetry import TelemetryClient
from argilla.server.database import Base, get_db
from argilla.server.models import User, UserRole, Workspace
from argilla.server.search_engine import SearchEngine, get_search_engine
from argilla.server.server import app, argilla_app
from argilla.server.settings import settings
from fastapi.testclient import TestClient
from opensearchpy import OpenSearch
from sqlalchemy import create_engine

from tests.database import TestSession
from tests.factories import (
    AnnotatorFactory,
    OwnerFactory,
    UserFactory,
)
from tests.helpers import SecuredClient

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture
    from sqlalchemy import Connection
    from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def connection() -> Generator["Connection", None, None]:
    # Create a temp directory to store a SQLite database used for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        database_url = f"sqlite:///{tmpdir}/test.db"
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        conn = engine.connect()
        TestSession.configure(bind=conn)
        Base.metadata.create_all(conn)

        yield conn

        Base.metadata.drop_all(conn)
        conn.close()
        engine.dispose()


@pytest.fixture(autouse=True)
def db(connection: "Connection") -> Generator["Session", None, None]:
    nested_transaction = connection.begin_nested()
    session = TestSession()

    yield session

    session.close()
    nested_transaction.rollback()


@pytest.fixture(scope="function")
def mock_search_engine(mocker) -> Generator["SearchEngine", None, None]:
    return mocker.AsyncMock(SearchEngine)


@pytest.fixture(scope="function")
def client(request, mock_search_engine: SearchEngine) -> Generator[TestClient, None, None]:
    session = TestSession()

    def override_get_db():
        yield session

    async def override_get_search_engine():
        yield mock_search_engine

    argilla_app.dependency_overrides[get_db] = override_get_db
    argilla_app.dependency_overrides[get_search_engine] = override_get_search_engine

    raise_server_exceptions = request.param if hasattr(request, "param") else False
    with TestClient(app, raise_server_exceptions=raise_server_exceptions) as client:
        yield client

    argilla_app.dependency_overrides.clear()


def is_running_elasticsearch() -> bool:
    open_search = OpenSearch(hosts=settings.elasticsearch)

    info = open_search.info(format="json")
    version_info = info["version"]

    return "distribution" not in version_info


@pytest.fixture(scope="session")
def elasticsearch_config():
    return {"hosts": settings.elasticsearch}


@pytest.fixture(scope="session")
def opensearch(elasticsearch_config):
    client = OpenSearch(**elasticsearch_config)
    yield client

    for index_info in client.cat.indices(index="ar.*,rg.*", format="json"):
        client.indices.delete(index=index_info["index"])


@pytest.fixture(scope="function")
def owner() -> User:
    return OwnerFactory.create(first_name="Owner", username="owner", api_key="owner.apikey")


@pytest.fixture(scope="function")
def annotator() -> User:
    return AnnotatorFactory.create(first_name="Annotator", username="annotator", api_key="annotator.apikey")


@pytest.fixture(scope="function")
def mock_user() -> User:
    return UserFactory.create(
        first_name="Mock",
        username="mock-user",
        password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
        api_key="mock-user.apikey",
    )


@pytest.fixture(scope="function")
def owner_auth_header(owner: User) -> Dict[str, str]:
    return {API_KEY_HEADER_NAME: owner.api_key}


@pytest.fixture(scope="function")
def argilla_user() -> User:
    user = UserFactory.create(
        first_name="Argilla",
        username="argilla",
        role=UserRole.admin,  # Force to use an admin user
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
def test_telemetry(mocker: "MockerFixture") -> "MagicMock":
    telemetry._CLIENT = TelemetryClient(disable_send=True)

    return mocker.spy(telemetry._CLIENT, "track_data")


@pytest.fixture(autouse=True)
def using_test_client_from_argilla_python_client(monkeypatch, test_telemetry: "MagicMock", client: TestClient):
    real_whoami = users_api.whoami

    def whoami_mocked(*args, **kwargs):
        client_arg = args[-1] if args else kwargs["client"]

        monkeypatch.setattr(client_arg, "__httpx__", client)
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
    monkeypatch, using_test_client_from_argilla_python_client, argilla_user: User, client: TestClient
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

    from argilla.client.api import active_api

    rb_api = active_api()
    monkeypatch.setattr(rb_api.http_client, "__httpx__", client_)

    return client_


@pytest.fixture
def dataset_token_classification(mocked_client):
    from datasets import load_dataset

    dataset = "gutenberg_spacy_ner"

    dataset_ds = load_dataset(
        "argilla/gutenberg_spacy-ner",
        split="train[:100]",
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

    delete(dataset)
    log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture
def dataset_text_classification(mocked_client):
    from datasets import load_dataset

    dataset = "banking_sentiment_setfit"

    dataset_ds = load_dataset(
        f"argilla/{dataset}",
        split="train[:100]",
    )
    dataset_rb = [TextClassificationRecord(text=rec["text"], annotation=rec["label"]) for rec in dataset_ds]
    labels = set([rec.annotation for rec in dataset_rb])
    configure_dataset(dataset, settings=TextClassificationSettings(label_schema=labels))

    delete(dataset)
    log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture
def dataset_text_classification_multi_label(mocked_client):
    from datasets import load_dataset

    dataset = "research_titles_multi_label"

    dataset_ds = load_dataset("argilla/research_titles_multi-label", split="train[:100]")

    dataset_rb = read_datasets(dataset_ds, task="TextClassification")

    dataset_rb = [rec for rec in dataset_rb if rec.annotation]

    delete(dataset)
    log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture
def dataset_text2text(mocked_client):
    from datasets import load_dataset

    dataset = "news_summary"

    dataset_ds = load_dataset("argilla/news-summary", split="train[:100]")

    records = []
    for entry in dataset_ds:
        records.append(Text2TextRecord(text=entry["text"], annotation=entry["prediction"][0]["text"]))

    delete(dataset)
    log(name=dataset, records=records)

    return dataset
