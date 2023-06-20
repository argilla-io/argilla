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

import pytest
from argilla._constants import DEFAULT_API_KEY
from argilla.client.client import Argilla
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.v1.datasets.api import (
    add_field,
    add_question,
    add_records,
    create_dataset,
    delete_dataset,
    get_dataset,
    get_fields,
    get_questions,
    get_records,
    list_datasets,
    publish_dataset,
)
from argilla.client.sdk.v1.datasets.models import (
    FeedbackDatasetModel,
    FeedbackFieldModel,
    FeedbackItemModel,
    FeedbackQuestionModel,
    FeedbackRecordsModel,
)
from argilla.server.models import DatasetStatus, UserRole

from tests.factories import (
    AdminFactory,
    DatasetFactory,
    RatingQuestionFactory,
    RecordFactory,
    TextFieldFactory,
    UserFactory,
    WorkspaceFactory,
)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner, UserRole.annotator])
def test_list_datasets(role: UserRole) -> None:
    dataset = DatasetFactory.create()
    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = list_datasets(client=api.client.httpx)

    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], FeedbackDatasetModel)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner, UserRole.annotator])
def test_get_datasets(role: UserRole) -> None:
    dataset = DatasetFactory.create()
    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = get_dataset(client=api.client.httpx, id=dataset.id)

    assert response.status_code == 200
    assert isinstance(response.parsed, FeedbackDatasetModel)
    assert response.parsed.name == dataset.name


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
def test_create_dataset(role: UserRole) -> None:
    workspace = WorkspaceFactory.create()

    user = UserFactory.create(role=role, workspaces=[workspace])

    api = Argilla(api_key=user.api_key, workspace=workspace.name)
    response = create_dataset(client=api.client.httpx, name="dataset_name", workspace_id=str(workspace.id))

    assert response.status_code == 201
    assert isinstance(response.parsed, FeedbackDatasetModel)
    assert response.parsed.name == "dataset_name"


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
def test_delete_dataset(role: UserRole):
    dataset = DatasetFactory.create()
    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = delete_dataset(client=api.client.httpx, id=dataset.id)

    assert response.status_code == 200

    response = api.client.httpx.get("/api/v1/me/datasets")
    assert response.status_code == 200
    assert len(response.json()["items"]) < 1


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
def test_publish_dataset(role: UserRole):
    dataset = DatasetFactory.create(fields=[TextFieldFactory.create()], questions=[RatingQuestionFactory.create()])
    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = publish_dataset(client=api.client.httpx, id=dataset.id)

    assert response.status_code == 200
    assert isinstance(response.parsed, FeedbackDatasetModel)
    assert response.parsed.name == dataset.name
    assert response.parsed.status == "ready"


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
def test_add_field(role: UserRole):
    dataset = DatasetFactory.create(fields=[TextFieldFactory.create()], questions=[RatingQuestionFactory.create()])
    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)

    response = add_field(
        client=api.client.httpx,
        id=dataset.id,
        field={"name": "test_field", "title": "text_field", "required": True, "settings": {"type": "text"}},
    )
    assert response.status_code == 201


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner, UserRole.annotator])
def test_get_fields(role: UserRole):
    dataset = DatasetFactory.create(fields=[TextFieldFactory.create()], questions=[RatingQuestionFactory.create()])
    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = get_fields(client=api.client.httpx, id=dataset.id)

    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], FeedbackFieldModel)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
def test_add_question(role: UserRole):
    dataset = DatasetFactory.create(fields=[TextFieldFactory.create()], questions=[RatingQuestionFactory.create()])
    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = add_question(
        client=api.client.httpx,
        id=dataset.id,
        question={
            "name": "test_question",
            "title": "text_question",
            "description": "test_description",
            "required": True,
            "settings": {"type": "text"},
        },
    )
    assert response.status_code == 201


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner, UserRole.annotator])
def test_get_questions(role: UserRole):
    dataset = DatasetFactory.create(fields=[TextFieldFactory.create()], questions=[RatingQuestionFactory.create()])
    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = get_questions(client=api.client.httpx, id=dataset.id)

    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], FeedbackQuestionModel)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
def test_add_records(role: UserRole):
    dataset = DatasetFactory.create(
        status=DatasetStatus.ready,
        fields=[TextFieldFactory.create(name="test_field")],
        questions=[RatingQuestionFactory.create()],
    )
    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = add_records(client=api.client.httpx, id=dataset.id, records=[{"fields": {"test_field": "test_value"}}])

    assert response.status_code == 204


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
def test_get_records(role: UserRole):
    dataset = DatasetFactory.create(
        status=DatasetStatus.ready,
        fields=[TextFieldFactory.create(name="test_field")],
        questions=[RatingQuestionFactory.create()],
        records=RecordFactory.create_batch(size=10),
    )
    user = UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = get_records(client=api.http_client.httpx, id=dataset.id)

    assert response.status_code == 200
    assert isinstance(response.parsed, FeedbackRecordsModel)
    assert len(response.parsed.items) > 0
    assert FeedbackItemModel(**response.parsed.items[0].dict())
