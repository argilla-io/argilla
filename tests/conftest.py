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
from unittest.mock import MagicMock

import argilla as rg
import httpx
import pytest
from argilla import app
from argilla._constants import API_KEY_HEADER_NAME, DEFAULT_API_KEY
from argilla.client.api import active_api
from argilla.client.apis.datasets import TextClassificationSettings
from argilla.client.client import Argilla
from argilla.client.sdk.users import api as users_api
from argilla.server.commons import telemetry
from argilla.server.commons.telemetry import TelemetryClient
from argilla.server.database import SessionLocal
from argilla.server.models import User, UserRole, Workspace, WorkspaceUser
from argilla.server.settings import settings
from opensearchpy import OpenSearch
from starlette.testclient import TestClient

from .factories import AdminFactory, AnnotatorFactory
from .helpers import SecuredClient


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def db():
    session = SessionLocal()
    # test_seeds(session)  # without a session, rollback is not working when some error occurs in a test

    yield session

    session.query(User).delete()
    session.query(Workspace).delete()
    session.query(WorkspaceUser).delete()
    session.commit()


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
def admin(db):
    return AdminFactory.create(first_name="Admin", username="admin", api_key="admin.apikey")


@pytest.fixture(scope="function")
def annotator(db):
    return AnnotatorFactory.create(first_name="Annotator", username="annotator", api_key="annotator.apikey")


@pytest.fixture
def mock_user(db):
    user = User(
        first_name="Mock",
        username="mock-user",
        password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
        api_key="mock-user.apikey",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture(scope="function")
def admin_auth_header(db, admin):
    return {API_KEY_HEADER_NAME: admin.api_key}


@pytest.fixture(scope="function")
def argilla_auth_header(db, argilla_user):
    return {API_KEY_HEADER_NAME: argilla_user.api_key}


@pytest.fixture
def argilla_user(db):
    user = User(
        first_name="Argilla",
        username="argilla",
        role=UserRole.admin,
        password_hash="$2y$05$eaw.j2Kaw8s8vpscVIZMfuqSIX3OLmxA21WjtWicDdn0losQ91Hw.",
        api_key=DEFAULT_API_KEY,
        workspaces=[Workspace(name="argilla")],
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def test_telemetry(mocker) -> MagicMock:
    telemetry.telemetry_client = TelemetryClient(disable_send=True)

    return mocker.spy(telemetry.telemetry_client, "track_data")


@pytest.fixture(scope="session")
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def api():
    return Argilla()


@pytest.fixture
def mocked_client(
    db,
    monkeypatch,
    test_telemetry,
    argilla_user,
) -> SecuredClient:
    with TestClient(app, raise_server_exceptions=False) as _client:
        client_ = SecuredClient(_client)

        real_whoami = users_api.whoami

        def whoami_mocked(client):
            monkeypatch.setattr(client, "__httpx__", client_)
            return real_whoami(client)

        monkeypatch.setattr(users_api, "whoami", whoami_mocked)

        monkeypatch.setattr(httpx, "post", client_.post)
        monkeypatch.setattr(httpx, "patch", client_.patch)
        monkeypatch.setattr(httpx.AsyncClient, "post", client_.post_async)
        monkeypatch.setattr(httpx, "get", client_.get)
        monkeypatch.setattr(httpx, "delete", client_.delete)
        monkeypatch.setattr(httpx, "put", client_.put)
        monkeypatch.setattr(httpx, "stream", client_.stream)

        rb_api = active_api()
        monkeypatch.setattr(rb_api._client, "__httpx__", client_)

        yield client_


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

    dataset_rb = rg.read_datasets(dataset_ds, task="TokenClassification")
    # Set annotations, required for training tests
    for rec in dataset_rb:
        # Strip off "score"
        rec.annotation = [prediction[:3] for prediction in rec.prediction]
        rec.annotation_agent = rec.prediction_agent
        rec.prediction = []
        rec.prediction_agent = None

    rg.delete(dataset)
    rg.log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture
def dataset_text_classification(mocked_client):
    from datasets import load_dataset

    dataset = "banking_sentiment_setfit"

    dataset_ds = load_dataset(
        f"argilla/{dataset}",
        split="train[:100]",
    )
    dataset_rb = [rg.TextClassificationRecord(text=rec["text"], annotation=rec["label"]) for rec in dataset_ds]
    labels = set([rec.annotation for rec in dataset_rb])
    rg.configure_dataset(dataset, settings=TextClassificationSettings(label_schema=labels))

    rg.delete(dataset)
    rg.log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture
def dataset_text_classification_multi_label(mocked_client):
    from datasets import load_dataset

    dataset = "research_titles_multi_label"

    dataset_ds = load_dataset("argilla/research_titles_multi-label", split="train[:100]")

    dataset_rb = rg.read_datasets(dataset_ds, task="TextClassification")

    dataset_rb = [rec for rec in dataset_rb if rec.annotation]

    rg.delete(dataset)
    rg.log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture
def dataset_text2text(mocked_client):
    from datasets import load_dataset

    dataset = "news_summary"

    dataset_ds = load_dataset("argilla/news-summary", split="train[:100]")

    records = []
    for entry in dataset_ds:
        records.append(rg.Text2TextRecord(text=entry["text"], annotation=entry["prediction"][0]["text"]))

    rg.delete(dataset)
    rg.log(name=dataset, records=records)

    return dataset
