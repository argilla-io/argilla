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

from datetime import datetime
from typing import List, Optional, Tuple, Type
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.apis.v1.handlers.datasets import LIST_DATASET_RECORDS_LIMIT_DEFAULT
from argilla.server.models import (
    Dataset,
    DatasetStatus,
    Field,
    Question,
    Record,
    Response,
    ResponseStatus,
    User,
    UserRole,
    Workspace,
)
from argilla.server.schemas.v1.datasets import (
    DATASET_CREATE_GUIDELINES_MAX_LENGTH,
    FIELD_CREATE_NAME_MAX_LENGTH,
    FIELD_CREATE_TITLE_MAX_LENGTH,
    QUESTION_CREATE_DESCRIPTION_MAX_LENGTH,
    QUESTION_CREATE_NAME_MAX_LENGTH,
    QUESTION_CREATE_TITLE_MAX_LENGTH,
    RATING_OPTIONS_MAX_ITEMS,
    RATING_OPTIONS_MIN_ITEMS,
    RECORDS_CREATE_MAX_ITEMS,
    RECORDS_CREATE_MIN_ITEMS,
    VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH,
    VALUE_TEXT_OPTION_TEXT_MAX_LENGTH,
    VALUE_TEXT_OPTION_VALUE_MAX_LENGTH,
    RecordInclude,
)
from argilla.server.search_engine import (
    Query,
    SearchEngine,
    SearchResponseItem,
    SearchResponses,
    TextQuery,
    UserResponseStatusFilter,
)
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import (
    AdminFactory,
    AnnotatorFactory,
    DatasetFactory,
    FieldFactory,
    LabelSelectionQuestionFactory,
    MultiLabelSelectionQuestionFactory,
    QuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    TextFieldFactory,
    TextQuestionFactory,
    UserFactory,
    WorkspaceFactory,
)


def test_list_current_user_datasets(client: TestClient, owner_auth_header):
    dataset_a = DatasetFactory.create(name="dataset-a")
    dataset_b = DatasetFactory.create(name="dataset-b", guidelines="guidelines")
    dataset_c = DatasetFactory.create(name="dataset-c", status=DatasetStatus.ready)

    response = client.get("/api/v1/me/datasets", headers=owner_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(dataset_a.id),
                "name": "dataset-a",
                "guidelines": None,
                "status": "draft",
                "workspace_id": str(dataset_a.workspace_id),
                "inserted_at": dataset_a.inserted_at.isoformat(),
                "updated_at": dataset_a.updated_at.isoformat(),
            },
            {
                "id": str(dataset_b.id),
                "name": "dataset-b",
                "guidelines": "guidelines",
                "status": "draft",
                "workspace_id": str(dataset_b.workspace_id),
                "inserted_at": dataset_b.inserted_at.isoformat(),
                "updated_at": dataset_b.updated_at.isoformat(),
            },
            {
                "id": str(dataset_c.id),
                "name": "dataset-c",
                "guidelines": None,
                "status": "ready",
                "workspace_id": str(dataset_c.workspace_id),
                "inserted_at": dataset_c.inserted_at.isoformat(),
                "updated_at": dataset_c.updated_at.isoformat(),
            },
        ]
    }


def test_list_current_user_datasets_without_authentication(client: TestClient):
    response = client.get("/api/v1/me/datasets")

    assert response.status_code == 401


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
def test_list_current_user_datasets_as_restricted_user_role(client: TestClient, role: UserRole):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create(workspaces=[workspace], role=role)

    DatasetFactory.create(name="dataset-a", workspace=workspace)
    DatasetFactory.create(name="dataset-b", workspace=workspace)
    DatasetFactory.create(name="dataset-c")

    response = client.get("/api/v1/me/datasets", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 200

    response_body = response.json()
    assert [dataset["name"] for dataset in response_body["items"]] == ["dataset-a", "dataset-b"]


def test_list_dataset_fields(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.build()
    text_field_a = TextFieldFactory.create(name="text-field-a", title="Text Field A", required=True, dataset=dataset)
    text_field_b = TextFieldFactory.create(name="text-field-b", title="Text Field B", dataset=dataset)

    other_dataset = DatasetFactory.create()
    TextFieldFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(text_field_a.id),
                "name": "text-field-a",
                "title": "Text Field A",
                "required": True,
                "settings": {"type": "text", "use_markdown": False},
                "inserted_at": text_field_a.inserted_at.isoformat(),
                "updated_at": text_field_a.updated_at.isoformat(),
            },
            {
                "id": str(text_field_b.id),
                "name": "text-field-b",
                "title": "Text Field B",
                "required": False,
                "settings": {"type": "text", "use_markdown": False},
                "inserted_at": text_field_b.inserted_at.isoformat(),
                "updated_at": text_field_b.updated_at.isoformat(),
            },
        ],
    }


def test_list_dataset_fields_without_authentication(client: TestClient):
    dataset = DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{dataset.id}/fields")

    assert response.status_code == 401


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
def test_list_dataset_fields_as_restricted_user_role(client: TestClient, role: UserRole):
    dataset = DatasetFactory.create()
    user = UserFactory.create(workspaces=[dataset.workspace], role=role)
    TextFieldFactory.create(name="text-field-a", dataset=dataset)
    TextFieldFactory.create(name="text-field-b", dataset=dataset)

    other_dataset = DatasetFactory.create()
    TextFieldFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/datasets/{dataset.id}/fields", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 200

    response_body = response.json()
    assert [field["name"] for field in response_body["items"]] == ["text-field-a", "text-field-b"]


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
def test_list_dataset_fields_as_restricted_user_from_different_workspace(client: TestClient, role: UserRole):
    dataset = DatasetFactory.create()
    user = UserFactory.create(workspaces=[WorkspaceFactory.build()], role=role)

    response = client.get(f"/api/v1/datasets/{dataset.id}/fields", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 403


def test_list_dataset_fields_with_nonexistent_dataset_id(client: TestClient, owner_auth_header):
    DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{uuid4()}/fields", headers=owner_auth_header)

    assert response.status_code == 404


def test_list_dataset_questions(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.create()
    text_question = TextQuestionFactory.create(
        name="text-question",
        title="Text Question",
        required=True,
        dataset=dataset,
    )
    rating_question = RatingQuestionFactory.create(
        name="rating-question",
        title="Rating Question",
        description="Rating Description",
        dataset=dataset,
    )
    TextQuestionFactory.create()
    RatingQuestionFactory.create()

    response = client.get(f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(text_question.id),
                "name": "text-question",
                "title": "Text Question",
                "description": "Question Description",
                "required": True,
                "settings": {"type": "text", "use_markdown": False},
                "inserted_at": text_question.inserted_at.isoformat(),
                "updated_at": text_question.updated_at.isoformat(),
            },
            {
                "id": str(rating_question.id),
                "name": "rating-question",
                "title": "Rating Question",
                "description": "Rating Description",
                "required": False,
                "settings": {
                    "type": "rating",
                    "options": [
                        {"value": 1},
                        {"value": 2},
                        {"value": 3},
                        {"value": 4},
                        {"value": 5},
                        {"value": 6},
                        {"value": 7},
                        {"value": 8},
                        {"value": 9},
                        {"value": 10},
                    ],
                },
                "inserted_at": rating_question.inserted_at.isoformat(),
                "updated_at": rating_question.updated_at.isoformat(),
            },
        ]
    }


@pytest.mark.parametrize(
    "QuestionFactory, settings",
    [
        (RatingQuestionFactory, {"options": [{"value": 1}, {"value": 2}, {"value": 2}]}),
        (
            LabelSelectionQuestionFactory,
            {
                "options": [
                    {"value": "a", "text": "a", "description": "a"},
                    {"value": "b", "text": "b", "description": "b"},
                    {"value": "b", "text": "b", "description": "b"},
                ],
                "visible_options": None,
            },
        ),
        (
            MultiLabelSelectionQuestionFactory,
            {
                "options": [
                    {"value": "a", "text": "a", "description": "a"},
                    {"value": "b", "text": "b", "description": "b"},
                    {"value": "b", "text": "b", "description": "b"},
                ],
                "visible_options": None,
            },
        ),
    ],
)
def test_list_dataset_questions_with_duplicate_values(
    client: TestClient, owner_auth_header, QuestionFactory: Type[QuestionFactory], settings: dict
):
    dataset = DatasetFactory.create()
    question = QuestionFactory.create(dataset=dataset, settings=settings)

    response = client.get(f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header)
    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(question.id),
                "name": question.name,
                "title": question.title,
                "description": question.description,
                "required": question.required,
                "settings": {"type": QuestionFactory.settings["type"], **settings},
                "inserted_at": question.inserted_at.isoformat(),
                "updated_at": question.updated_at.isoformat(),
            }
        ]
    }


def test_list_dataset_questions_without_authentication(client: TestClient):
    dataset = DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{dataset.id}/questions")

    assert response.status_code == 401


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
def test_list_dataset_questions_as_restricted_user(client: TestClient, role: UserRole):
    dataset = DatasetFactory.create()
    user = UserFactory.create(workspaces=[dataset.workspace], role=role)
    TextQuestionFactory.create(name="text-question", dataset=dataset)
    RatingQuestionFactory.create(name="rating-question", dataset=dataset)
    TextQuestionFactory.create()
    RatingQuestionFactory.create()

    response = client.get(f"/api/v1/datasets/{dataset.id}/questions", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 200

    response_body = response.json()
    assert [question["name"] for question in response_body["items"]] == ["text-question", "rating-question"]


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
def test_list_dataset_questions_as_restricted_user_from_different_workspace(client: TestClient, role: UserRole):
    dataset = DatasetFactory.create()
    user = UserFactory.create(workspaces=[WorkspaceFactory.build()], role=role)

    response = client.get(f"/api/v1/datasets/{dataset.id}/questions", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 403


def test_list_dataset_questions_with_nonexistent_dataset_id(client: TestClient, owner_auth_header):
    DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{uuid4()}/questions", headers=owner_auth_header)

    assert response.status_code == 404


def test_list_dataset_records(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.create()
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_b = RecordFactory.create(fields={"record_b": "value_b"}, metadata_={"unit": "test"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(record_a.id),
                "fields": {"record_a": "value_a"},
                "metadata": None,
                "external_id": record_a.external_id,
                "inserted_at": record_a.inserted_at.isoformat(),
                "updated_at": record_a.updated_at.isoformat(),
            },
            {
                "id": str(record_b.id),
                "fields": {"record_b": "value_b"},
                "metadata": {"unit": "test"},
                "external_id": record_b.external_id,
                "inserted_at": record_b.inserted_at.isoformat(),
                "updated_at": record_b.updated_at.isoformat(),
            },
            {
                "id": str(record_c.id),
                "fields": {"record_c": "value_c"},
                "metadata": None,
                "external_id": record_c.external_id,
                "inserted_at": record_c.inserted_at.isoformat(),
                "updated_at": record_c.updated_at.isoformat(),
            },
        ],
    }


def test_list_dataset_records_with_include_responses(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.create()
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_b = RecordFactory.create(fields={"record_b": "value_b"}, metadata_={"unit": "test"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    response_a = ResponseFactory.create(
        values={
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        record=record_a,
    )

    response_b_1 = ResponseFactory.create(
        values={
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "no"},
        },
        record=record_b,
    )
    response_b_2 = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        record=record_b,
    )

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(
        f"/api/v1/datasets/{dataset.id}/records",
        params={"include": RecordInclude.responses.value},
        headers=owner_auth_header,
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(record_a.id),
                "fields": {"record_a": "value_a"},
                "metadata": None,
                "external_id": record_a.external_id,
                "responses": [
                    {
                        "id": str(response_a.id),
                        "values": {
                            "input_ok": {"value": "yes"},
                            "output_ok": {"value": "yes"},
                        },
                        "status": "submitted",
                        "user_id": str(response_a.user_id),
                        "inserted_at": response_a.inserted_at.isoformat(),
                        "updated_at": response_a.updated_at.isoformat(),
                    },
                ],
                "inserted_at": record_a.inserted_at.isoformat(),
                "updated_at": record_a.updated_at.isoformat(),
            },
            {
                "id": str(record_b.id),
                "fields": {"record_b": "value_b"},
                "metadata": {"unit": "test"},
                "external_id": record_b.external_id,
                "responses": [
                    {
                        "id": str(response_b_1.id),
                        "values": {
                            "input_ok": {"value": "yes"},
                            "output_ok": {"value": "no"},
                        },
                        "status": "submitted",
                        "user_id": str(response_b_1.user_id),
                        "inserted_at": response_b_1.inserted_at.isoformat(),
                        "updated_at": response_b_1.updated_at.isoformat(),
                    },
                    {
                        "id": str(response_b_2.id),
                        "values": {
                            "input_ok": {"value": "no"},
                            "output_ok": {"value": "no"},
                        },
                        "status": "submitted",
                        "user_id": str(response_b_2.user_id),
                        "inserted_at": response_b_2.inserted_at.isoformat(),
                        "updated_at": response_b_2.updated_at.isoformat(),
                    },
                ],
                "inserted_at": record_b.inserted_at.isoformat(),
                "updated_at": record_b.updated_at.isoformat(),
            },
            {
                "id": str(record_c.id),
                "fields": {"record_c": "value_c"},
                "metadata": None,
                "external_id": record_c.external_id,
                "responses": [],
                "inserted_at": record_c.inserted_at.isoformat(),
                "updated_at": record_c.updated_at.isoformat(),
            },
        ],
    }


def test_list_dataset_records_with_offset(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.create()
    RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, params={"offset": 2})

    assert response.status_code == 200

    response_body = response.json()
    assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]


def test_list_dataset_records_with_limit(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.create()
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, params={"limit": 1})

    assert response.status_code == 200

    response_body = response.json()
    assert [item["id"] for item in response_body["items"]] == [str(record_a.id)]


def test_list_dataset_records_with_offset_and_limit(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.create()
    RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(
        f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, params={"offset": 1, "limit": 1}
    )

    assert response.status_code == 200

    response_body = response.json()
    assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]


def test_list_dataset_records_without_authentication(client: TestClient):
    dataset = DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{dataset.id}/records")

    assert response.status_code == 401


def test_list_dataset_records_as_admin(client: TestClient):
    workspace = WorkspaceFactory.create()
    admin = AdminFactory.create(workspaces=[workspace])
    dataset = DatasetFactory.create(workspace=workspace)

    RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: admin.api_key})
    assert response.status_code == 200


def test_list_dataset_records_as_annotator(client: TestClient):
    workspace = WorkspaceFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[workspace])
    dataset = DatasetFactory.create(workspace=workspace)

    RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: annotator.api_key})
    assert response.status_code == 403


def test_list_current_user_dataset_records(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.create()
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_b = RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, metadata_={"unit": "test"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/records", headers=owner_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(record_a.id),
                "fields": {"record_a": "value_a"},
                "metadata": None,
                "external_id": record_a.external_id,
                "inserted_at": record_a.inserted_at.isoformat(),
                "updated_at": record_a.updated_at.isoformat(),
            },
            {
                "id": str(record_b.id),
                "fields": {"record_b": "value_b"},
                "metadata": None,
                "external_id": record_b.external_id,
                "inserted_at": record_b.inserted_at.isoformat(),
                "updated_at": record_b.updated_at.isoformat(),
            },
            {
                "id": str(record_c.id),
                "fields": {"record_c": "value_c"},
                "metadata": {"unit": "test"},
                "external_id": record_c.external_id,
                "inserted_at": record_c.inserted_at.isoformat(),
                "updated_at": record_c.updated_at.isoformat(),
            },
        ],
    }


def test_list_current_user_dataset_records_with_include_responses(client: TestClient, owner, owner_auth_header: dict):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[dataset.workspace])
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_b = RecordFactory.create(fields={"record_b": "value_b"}, metadata_={"unit": "test"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    response_a_annotator = ResponseFactory.create(
        values={
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        record=record_a,
        user=annotator,
    )
    response_a_owner = ResponseFactory.create(
        status="discarded",
        record=record_a,
        user=owner,
    )
    response_b_annotator = ResponseFactory.create(
        values={
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "no"},
        },
        record=record_b,
        user=annotator,
    )
    response_b_owner = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        record=record_b,
        user=owner,
    )
    response_b_other = ResponseFactory.create(
        values={
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        record=record_b,
    )

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(
        f"/api/v1/me/datasets/{dataset.id}/records",
        params={"include": RecordInclude.responses.value},
        headers=owner_auth_header,
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(record_a.id),
                "fields": {"record_a": "value_a"},
                "metadata": None,
                "external_id": record_a.external_id,
                "responses": [
                    {
                        "id": str(response_a_owner.id),
                        "values": None,
                        "status": "discarded",
                        "user_id": str(owner.id),
                        "inserted_at": response_a_owner.inserted_at.isoformat(),
                        "updated_at": response_a_owner.updated_at.isoformat(),
                    }
                ],
                "inserted_at": record_a.inserted_at.isoformat(),
                "updated_at": record_a.updated_at.isoformat(),
            },
            {
                "id": str(record_b.id),
                "fields": {"record_b": "value_b"},
                "metadata": {"unit": "test"},
                "external_id": record_b.external_id,
                "responses": [
                    {
                        "id": str(response_b_owner.id),
                        "values": {
                            "input_ok": {"value": "no"},
                            "output_ok": {"value": "no"},
                        },
                        "status": "submitted",
                        "user_id": str(owner.id),
                        "inserted_at": response_b_owner.inserted_at.isoformat(),
                        "updated_at": response_b_owner.updated_at.isoformat(),
                    },
                ],
                "inserted_at": record_b.inserted_at.isoformat(),
                "updated_at": record_b.updated_at.isoformat(),
            },
            {
                "id": str(record_c.id),
                "fields": {"record_c": "value_c"},
                "metadata": None,
                "external_id": record_c.external_id,
                "responses": [],
                "inserted_at": record_c.inserted_at.isoformat(),
                "updated_at": record_c.updated_at.isoformat(),
            },
        ],
    }


def test_list_current_user_dataset_records_with_offset(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.create()
    RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/records", headers=owner_auth_header, params={"offset": 2})

    assert response.status_code == 200

    response_body = response.json()
    assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]


def test_list_current_user_dataset_records_with_limit(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.create()
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/records", headers=owner_auth_header, params={"limit": 1})

    assert response.status_code == 200

    response_body = response.json()
    assert [item["id"] for item in response_body["items"]] == [str(record_a.id)]


def test_list_current_user_dataset_records_with_offset_and_limit(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.create()
    RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(
        f"/api/v1/me/datasets/{dataset.id}/records", headers=owner_auth_header, params={"offset": 1, "limit": 1}
    )

    assert response.status_code == 200

    response_body = response.json()
    assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]


def create_records_with_response(
    num_records: int,
    dataset: Dataset,
    user: User,
    response_status: ResponseStatus,
    response_values: Optional[dict] = None,
):
    for record in RecordFactory.create_batch(size=num_records, dataset=dataset):
        ResponseFactory.create(record=record, user=user, values=response_values, status=response_status)


@pytest.mark.parametrize("response_status_filter", ["missing", "discarded", "submitted", "draft"])
def test_list_current_user_dataset_records_with_response_status_filter(
    client: TestClient, owner, owner_auth_header, response_status_filter: str
):
    num_responses_per_status = 10
    response_values = {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}}

    dataset = DatasetFactory.create()
    # missing responses
    RecordFactory.create_batch(size=num_responses_per_status, dataset=dataset)
    # discarded responses
    create_records_with_response(num_responses_per_status, dataset, owner, ResponseStatus.discarded)
    # submitted responses
    create_records_with_response(num_responses_per_status, dataset, owner, ResponseStatus.submitted, response_values)
    # drafted responses
    create_records_with_response(num_responses_per_status, dataset, owner, ResponseStatus.draft, response_values)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(
        f"/api/v1/me/datasets/{dataset.id}/records?response_status={response_status_filter}&include=responses",
        headers=owner_auth_header,
    )

    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json["items"]) == num_responses_per_status

    if response_status_filter == "missing":
        assert all([len(record["responses"]) == 0 for record in response_json["items"]])
    else:
        assert all([record["responses"][0]["status"] == response_status_filter for record in response_json["items"]])


def test_list_current_user_dataset_records_without_authentication(client: TestClient):
    dataset = DatasetFactory.create()

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/records")

    assert response.status_code == 401


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
def test_list_current_user_dataset_records_as_restricted_user(client: TestClient, role: UserRole):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create(workspaces=[workspace], role=role)
    dataset = DatasetFactory.create(workspace=workspace)
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_b = RecordFactory.create(fields={"record_b": "value_b"}, metadata_={"unit": "test"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(record_a.id),
                "fields": {"record_a": "value_a"},
                "metadata": None,
                "external_id": record_a.external_id,
                "inserted_at": record_a.inserted_at.isoformat(),
                "updated_at": record_a.updated_at.isoformat(),
            },
            {
                "id": str(record_b.id),
                "fields": {"record_b": "value_b"},
                "metadata": {"unit": "test"},
                "external_id": record_b.external_id,
                "inserted_at": record_b.inserted_at.isoformat(),
                "updated_at": record_b.updated_at.isoformat(),
            },
            {
                "id": str(record_c.id),
                "fields": {"record_c": "value_c"},
                "metadata": None,
                "external_id": record_c.external_id,
                "inserted_at": record_c.inserted_at.isoformat(),
                "updated_at": record_c.updated_at.isoformat(),
            },
        ],
    }


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
def test_list_current_user_dataset_records_as_restricted_user_with_include_responses(
    client: TestClient, owner: User, role: UserRole
):
    dataset = DatasetFactory.create()

    user = UserFactory.create(workspaces=[dataset.workspace], role=role)
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_b = RecordFactory.create(fields={"record_b": "value_b"}, metadata_={"unit": "test"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    response_a_owner = ResponseFactory.create(
        values={
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        record=record_a,
        user=owner,
    )
    response_a_annotator = ResponseFactory.create(
        status="discarded",
        record=record_a,
        user=user,
    )
    response_b_owner = ResponseFactory.create(
        values={
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "no"},
        },
        record=record_b,
        user=owner,
    )
    response_b_annotator = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        record=record_b,
        user=user,
    )
    response_b_other = ResponseFactory.create(
        values={
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        record=record_b,
    )

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(
        f"/api/v1/me/datasets/{dataset.id}/records",
        params={"include": RecordInclude.responses.value},
        headers={API_KEY_HEADER_NAME: user.api_key},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(record_a.id),
                "fields": {"record_a": "value_a"},
                "metadata": None,
                "external_id": record_a.external_id,
                "responses": [
                    {
                        "id": str(response_a_annotator.id),
                        "values": None,
                        "status": "discarded",
                        "user_id": str(user.id),
                        "inserted_at": response_a_annotator.inserted_at.isoformat(),
                        "updated_at": response_a_annotator.updated_at.isoformat(),
                    }
                ],
                "inserted_at": record_a.inserted_at.isoformat(),
                "updated_at": record_a.updated_at.isoformat(),
            },
            {
                "id": str(record_b.id),
                "fields": {"record_b": "value_b"},
                "metadata": {"unit": "test"},
                "external_id": record_b.external_id,
                "responses": [
                    {
                        "id": str(response_b_annotator.id),
                        "values": {
                            "input_ok": {"value": "no"},
                            "output_ok": {"value": "no"},
                        },
                        "status": "submitted",
                        "user_id": str(user.id),
                        "inserted_at": response_b_annotator.inserted_at.isoformat(),
                        "updated_at": response_b_annotator.updated_at.isoformat(),
                    },
                ],
                "inserted_at": record_b.inserted_at.isoformat(),
                "updated_at": record_b.updated_at.isoformat(),
            },
            {
                "id": str(record_c.id),
                "fields": {"record_c": "value_c"},
                "metadata": None,
                "external_id": record_c.external_id,
                "responses": [],
                "inserted_at": record_c.inserted_at.isoformat(),
                "updated_at": record_c.updated_at.isoformat(),
            },
        ],
    }


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
def test_list_current_user_dataset_records_as_restricted_user_from_different_workspace(
    client: TestClient, role: UserRole
):
    dataset = DatasetFactory.create()
    user = UserFactory.create(workspaces=[WorkspaceFactory.build()], role=role)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 403


def test_list_current_user_dataset_records_with_nonexistent_dataset_id(client: TestClient, owner_auth_header):
    DatasetFactory.create()

    response = client.get(f"/api/v1/me/datasets/{uuid4()}/records", headers=owner_auth_header)

    assert response.status_code == 404


def test_get_dataset(client: TestClient, owner_auth_header):
    dataset = DatasetFactory.create(name="dataset")

    response = client.get(f"/api/v1/datasets/{dataset.id}", headers=owner_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "id": str(dataset.id),
        "name": "dataset",
        "guidelines": None,
        "status": "draft",
        "workspace_id": str(dataset.workspace_id),
        "inserted_at": dataset.inserted_at.isoformat(),
        "updated_at": dataset.updated_at.isoformat(),
    }


def test_get_dataset_without_authentication(client: TestClient):
    dataset = DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{dataset.id}")

    assert response.status_code == 401


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
def test_get_dataset_as_restricted_user(client: TestClient, role: UserRole):
    dataset = DatasetFactory.create(name="dataset")
    user = UserFactory.create(workspaces=[dataset.workspace], role=role)

    response = client.get(f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 200
    assert response.json()["name"] == "dataset"


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
def test_get_dataset_as_restricted_user_from_different_workspace(client: TestClient, role: UserRole):
    dataset = DatasetFactory.create()
    user = UserFactory.create(workspaces=[WorkspaceFactory.build()], role=role)

    response = client.get(f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 403


def test_get_dataset_with_nonexistent_dataset_id(client: TestClient, owner_auth_header):
    DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{uuid4()}", headers=owner_auth_header)

    assert response.status_code == 404


def test_get_current_user_dataset_metrics(client: TestClient, owner, owner_auth_header):
    dataset = DatasetFactory.create()
    record_a = RecordFactory.create(dataset=dataset)
    record_b = RecordFactory.create(dataset=dataset)
    record_c = RecordFactory.create(dataset=dataset)
    record_d = RecordFactory.create(dataset=dataset)
    RecordFactory.create_batch(3, dataset=dataset)
    ResponseFactory.create(record=record_a, user=owner)
    ResponseFactory.create(record=record_b, user=owner, status=ResponseStatus.discarded)
    ResponseFactory.create(record=record_c, user=owner, status=ResponseStatus.discarded)
    ResponseFactory.create(record=record_d, user=owner, status=ResponseStatus.draft)

    other_dataset = DatasetFactory.create()
    other_record_a = RecordFactory.create(dataset=other_dataset)
    other_record_b = RecordFactory.create(dataset=other_dataset)
    other_record_c = RecordFactory.create(dataset=other_dataset)
    RecordFactory.create_batch(2, dataset=other_dataset)
    ResponseFactory.create(record=other_record_a, user=owner)
    ResponseFactory.create(record=other_record_b)
    ResponseFactory.create(record=other_record_c, status=ResponseStatus.discarded)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/metrics", headers=owner_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "records": {
            "count": 7,
        },
        "responses": {
            "count": 4,
            "submitted": 1,
            "discarded": 2,
            "draft": 1,
        },
    }


def test_get_current_user_dataset_metrics_without_authentication(client: TestClient):
    dataset = DatasetFactory.create()

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/metrics")

    assert response.status_code == 401


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
def test_get_current_user_dataset_metrics_as_restricted_user(client: TestClient, role: UserRole):
    dataset = DatasetFactory.create()
    user = UserFactory.create(workspaces=[dataset.workspace], role=role)
    record_a = RecordFactory.create(dataset=dataset)
    record_b = RecordFactory.create(dataset=dataset)
    record_c = RecordFactory.create(dataset=dataset)
    record_d = RecordFactory.create(dataset=dataset)
    RecordFactory.create_batch(2, dataset=dataset)
    ResponseFactory.create(record=record_a, user=user)
    ResponseFactory.create(record=record_b, user=user)
    ResponseFactory.create(record=record_c, user=user, status=ResponseStatus.discarded)
    ResponseFactory.create(record=record_d, user=user, status=ResponseStatus.draft)

    other_dataset = DatasetFactory.create()
    other_record_a = RecordFactory.create(dataset=other_dataset)
    other_record_b = RecordFactory.create(dataset=other_dataset)
    other_record_c = RecordFactory.create(dataset=other_dataset)
    RecordFactory.create_batch(3, dataset=other_dataset)
    ResponseFactory.create(record=other_record_a, user=user)
    ResponseFactory.create(record=other_record_b)
    ResponseFactory.create(record=other_record_c, status=ResponseStatus.discarded)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/metrics", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 200
    assert response.json() == {
        "records": {"count": 6},
        "responses": {"count": 4, "submitted": 2, "discarded": 1, "draft": 1},
    }


@pytest.mark.parametrize("role", [UserRole.annotator, UserRole.admin])
def test_get_current_user_dataset_metrics_restricted_user_from_different_workspace(client: TestClient, role: UserRole):
    dataset = DatasetFactory.create()
    user = UserFactory.create(workspaces=[WorkspaceFactory.build()], role=role)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/metrics", headers={API_KEY_HEADER_NAME: user.api_key})

    assert response.status_code == 403


def test_get_current_user_dataset_metrics_with_nonexistent_dataset_id(client: TestClient, owner_auth_header):
    DatasetFactory.create()

    response = client.get(f"/api/v1/me/datasets/{uuid4()}/metrics", headers=owner_auth_header)

    assert response.status_code == 404


def test_create_dataset(client: TestClient, db: Session, owner_auth_header):
    workspace = WorkspaceFactory.create()
    dataset_json = {"name": "name", "guidelines": "guidelines", "workspace_id": str(workspace.id)}

    response = client.post("/api/v1/datasets", headers=owner_auth_header, json=dataset_json)

    assert response.status_code == 201
    assert db.query(Dataset).count() == 1

    response_body = response.json()
    assert db.get(Dataset, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "name": "name",
        "guidelines": "guidelines",
        "status": "draft",
        "workspace_id": str(workspace.id),
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_create_dataset_with_invalid_length_guidelines(client: TestClient, db: Session, owner_auth_header):
    workspace = WorkspaceFactory.create()
    dataset_json = {
        "name": "name",
        "guidelines": "a" * (DATASET_CREATE_GUIDELINES_MAX_LENGTH + 1),
        "workspace_id": str(workspace.id),
    }

    response = client.post("/api/v1/datasets", headers=owner_auth_header, json=dataset_json)

    assert response.status_code == 422
    assert db.query(Dataset).count() == 0


def test_create_dataset_without_authentication(client: TestClient, db: Session):
    dataset_json = {"name": "name", "workspace_id": str(WorkspaceFactory.create().id)}

    response = client.post("/api/v1/datasets", json=dataset_json)

    assert response.status_code == 401
    assert db.query(Dataset).count() == 0


def test_create_dataset_as_admin(client: TestClient, db: Session):
    workspace = WorkspaceFactory.create()
    admin = AdminFactory.create(workspaces=[workspace])

    dataset_json = {"name": "name", "workspace_id": str(workspace.id)}
    response = client.post("/api/v1/datasets", headers={API_KEY_HEADER_NAME: admin.api_key}, json=dataset_json)

    assert response.status_code == 201
    assert db.query(Dataset).count() == 1


def test_create_dataset_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    dataset_json = {"name": "name", "workspace_id": str(WorkspaceFactory.create().id)}

    response = client.post("/api/v1/datasets", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=dataset_json)

    assert response.status_code == 403
    assert db.query(Dataset).count() == 0


def test_create_dataset_with_existent_name(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(name="name")
    dataset_json = {"name": "name", "workspace_id": str(dataset.workspace_id)}

    response = client.post("/api/v1/datasets", headers=owner_auth_header, json=dataset_json)

    assert response.status_code == 409
    assert db.query(Dataset).count() == 1


def test_create_dataset_with_nonexistent_workspace_id(client: TestClient, db: Session, owner_auth_header):
    dataset_json = {"name": "name", "workspace_id": str(uuid4())}

    response = client.post("/api/v1/datasets", headers=owner_auth_header, json=dataset_json)

    assert response.status_code == 422
    assert db.query(Dataset).count() == 0


@pytest.mark.parametrize(
    ("settings", "expected_settings"),
    [
        ({"type": "text"}, {"type": "text", "use_markdown": False}),
        ({"type": "text", "discarded": "value"}, {"type": "text", "use_markdown": False}),
        ({"type": "text", "use_markdown": False}, {"type": "text", "use_markdown": False}),
    ],
)
def test_create_dataset_field(
    client: TestClient,
    db: Session,
    owner_auth_header,
    settings: dict,
    expected_settings: dict,
):
    dataset = DatasetFactory.create()
    field_json = {"name": "name", "title": "title", "settings": settings}

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json)

    assert response.status_code == 201
    assert db.query(Field).count() == 1

    response_body = response.json()
    assert db.get(Field, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "name": "name",
        "title": "title",
        "required": False,
        "settings": expected_settings,
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_create_dataset_field_without_authentication(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    field_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", json=field_json)

    assert response.status_code == 401
    assert db.query(Field).count() == 0


def test_create_dataset_field_as_admin(client: TestClient, db: Session):
    workspace = WorkspaceFactory.create()
    admin = AdminFactory.create(workspaces=[workspace])
    dataset = DatasetFactory.create(workspace=workspace)
    field_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/fields",
        headers={API_KEY_HEADER_NAME: admin.api_key},
        json=field_json,
    )

    assert response.status_code == 201
    assert db.query(Field).count() == 1


def test_create_dataset_field_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    dataset = DatasetFactory.create()
    field_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/fields",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
        json=field_json,
    )

    assert response.status_code == 403
    assert db.query(Field).count() == 0


@pytest.mark.parametrize("invalid_name", ["", " ", "  ", "-", "--", "_", "__", "A", "AA", "invalid_nAmE"])
def test_create_dataset_field_with_invalid_name(client: TestClient, db: Session, owner_auth_header, invalid_name: str):
    dataset = DatasetFactory.create()
    field_json = {
        "name": invalid_name,
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json)

    assert response.status_code == 422
    assert db.query(Field).count() == 0


def test_create_dataset_field_with_invalid_max_length_name(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create()
    field_json = {
        "name": "a" * (FIELD_CREATE_NAME_MAX_LENGTH + 1),
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json)

    assert response.status_code == 422
    assert db.query(Field).count() == 0


def test_create_dataset_field_with_invalid_max_length_title(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create()
    field_json = {
        "name": "name",
        "title": "a" * (FIELD_CREATE_TITLE_MAX_LENGTH + 1),
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json)

    assert response.status_code == 422
    assert db.query(Field).count() == 0


@pytest.mark.parametrize(
    "settings",
    [
        {},
        None,
        {"type": "wrong-type"},
        {"type": "text", "use_markdown": None},
        {"type": "rating", "options": None},
        {"type": "rating", "options": []},
    ],
)
def test_create_dataset_field_with_invalid_settings(client: TestClient, db: Session, owner_auth_header, settings: dict):
    dataset = DatasetFactory.create()
    field_json = {
        "name": "name",
        "title": "Title",
        "settings": settings,
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json)

    assert response.status_code == 422
    assert db.query(Field).count() == 0


def test_create_dataset_field_with_existent_name(client: TestClient, db: Session, owner_auth_header):
    field = FieldFactory.create(name="name")
    field_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{field.dataset.id}/fields", headers=owner_auth_header, json=field_json)

    assert response.status_code == 409
    assert db.query(Field).count() == 1


def test_create_dataset_field_with_published_dataset(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    field_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=owner_auth_header, json=field_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Field cannot be created for a published dataset"}
    assert db.query(Field).count() == 0


def test_create_dataset_field_with_nonexistent_dataset_id(client: TestClient, db: Session, owner_auth_header):
    DatasetFactory.create()
    field_json = {
        "name": "text",
        "title": "Text",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{uuid4()}/fields", headers=owner_auth_header, json=field_json)

    assert response.status_code == 404
    assert db.query(Field).count() == 0


@pytest.mark.parametrize(
    ("settings", "expected_settings"),
    [
        ({"type": "text"}, {"type": "text", "use_markdown": False}),
        ({"type": "text", "use_markdown": True}, {"type": "text", "use_markdown": True}),
        ({"type": "text", "use_markdown": False}, {"type": "text", "use_markdown": False}),
        (
            {
                "type": "rating",
                "options": [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}],
            },
            {
                "type": "rating",
                "options": [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}],
            },
        ),
        (
            {
                "type": "label_selection",
                "options": [
                    {"value": "positive", "text": "Positive", "description": "Texts with positive sentiment"},
                    {"value": "negative", "text": "Negative", "description": "Texts with negative sentiment"},
                    {"value": "neutral", "text": "Neutral", "description": "Texts with neutral sentiment"},
                ],
                "visible_options": 10,
            },
            {
                "type": "label_selection",
                "options": [
                    {"value": "positive", "text": "Positive", "description": "Texts with positive sentiment"},
                    {"value": "negative", "text": "Negative", "description": "Texts with negative sentiment"},
                    {"value": "neutral", "text": "Neutral", "description": "Texts with neutral sentiment"},
                ],
                "visible_options": 10,
            },
        ),
        (
            {
                "type": "label_selection",
                "options": [
                    {"value": "positive", "text": "Positive"},
                    {"value": "negative", "text": "Negative"},
                    {"value": "neutral", "text": "Neutral"},
                ],
            },
            {
                "type": "label_selection",
                "options": [
                    {"value": "positive", "text": "Positive", "description": None},
                    {"value": "negative", "text": "Negative", "description": None},
                    {"value": "neutral", "text": "Neutral", "description": None},
                ],
                "visible_options": None,
            },
        ),
        (
            {
                "type": "ranking",
                "options": [
                    {"value": "completion-a", "text": "Completion A", "description": "Completion A is the best"},
                    {"value": "completion-b", "text": "Completion B", "description": "Completion B is the best"},
                    {"value": "completion-c", "text": "Completion C", "description": "Completion C is the best"},
                    {"value": "completion-d", "text": "Completion D", "description": "Completion D is the best"},
                ],
            },
            {
                "type": "ranking",
                "options": [
                    {"value": "completion-a", "text": "Completion A", "description": "Completion A is the best"},
                    {"value": "completion-b", "text": "Completion B", "description": "Completion B is the best"},
                    {"value": "completion-c", "text": "Completion C", "description": "Completion C is the best"},
                    {"value": "completion-d", "text": "Completion D", "description": "Completion D is the best"},
                ],
            },
        ),
        (
            {
                "type": "ranking",
                "options": [
                    {"value": "completion-a", "text": "Completion A", "description": None},
                    {"value": "completion-b", "text": "Completion b", "description": None},
                    {"value": "completion-c", "text": "Completion C", "description": None},
                    {"value": "completion-d", "text": "Completion D", "description": None},
                ],
            },
            {
                "type": "ranking",
                "options": [
                    {"value": "completion-a", "text": "Completion A", "description": None},
                    {"value": "completion-b", "text": "Completion b", "description": None},
                    {"value": "completion-c", "text": "Completion C", "description": None},
                    {"value": "completion-d", "text": "Completion D", "description": None},
                ],
            },
        ),
    ],
)
def test_create_dataset_question(
    client: TestClient,
    db: Session,
    owner_auth_header,
    settings: dict,
    expected_settings: dict,
):
    dataset = DatasetFactory.create()
    question_json = {
        "name": "name",
        "title": "title",
        "settings": settings,
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json)

    assert response.status_code == 201
    assert db.query(Question).count() == 1

    response_body = response.json()
    assert db.get(Question, UUID(response_body["id"]))
    assert response_body == {
        "id": str(UUID(response_body["id"])),
        "name": "name",
        "title": "title",
        "description": None,
        "required": False,
        "settings": expected_settings,
        "inserted_at": datetime.fromisoformat(response_body["inserted_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(response_body["updated_at"]).isoformat(),
    }


def test_create_dataset_question_with_description(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create()
    question_json = {
        "name": "name",
        "title": "title",
        "description": "description",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json)

    assert response.status_code == 201
    assert db.query(Question).count() == 1

    response_body = response.json()
    assert db.get(Question, UUID(response_body["id"]))
    assert response_body["description"] == "description"


def test_create_dataset_question_without_authentication(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    question_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", json=question_json)

    assert response.status_code == 401
    assert db.query(Question).count() == 0


def test_create_dataset_question_as_admin(client: TestClient, db: Session):
    workspace = WorkspaceFactory.create()
    admin = AdminFactory.create(workspaces=[workspace])
    dataset = DatasetFactory.create(workspace=workspace)
    question_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/questions",
        headers={API_KEY_HEADER_NAME: admin.api_key},
        json=question_json,
    )

    assert response.status_code == 201
    assert db.query(Question).count() == 1


def test_create_dataset_question_as_admin_for_different_workspace(client: TestClient, db: Session):
    workspace = WorkspaceFactory.create()
    admin = AdminFactory.create(workspaces=[workspace])

    dataset = DatasetFactory.create()
    question_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/questions",
        headers={API_KEY_HEADER_NAME: admin.api_key},
        json=question_json,
    )

    assert response.status_code == 403
    assert db.query(Question).count() == 0


def test_create_dataset_question_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    dataset = DatasetFactory.create()
    question_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/questions",
        headers={API_KEY_HEADER_NAME: annotator.api_key},
        json=question_json,
    )

    assert response.status_code == 403
    assert db.query(Question).count() == 0


@pytest.mark.parametrize("invalid_name", ["", " ", "  ", "-", "--", "_", "__", "A", "AA", "invalid_nAmE"])
def test_create_dataset_question_with_invalid_name(
    client: TestClient, db: Session, owner_auth_header, invalid_name: str
):
    dataset = DatasetFactory.create()
    question_json = {
        "name": invalid_name,
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json)

    assert response.status_code == 422
    assert db.query(Question).count() == 0


def test_create_dataset_question_with_invalid_max_length_name(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create()
    question_json = {
        "name": "a" * (QUESTION_CREATE_NAME_MAX_LENGTH + 1),
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json)

    assert response.status_code == 422
    assert db.query(Question).count() == 0


def test_create_dataset_question_with_invalid_max_length_title(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create()
    question_json = {
        "name": "name",
        "title": "a" * (QUESTION_CREATE_TITLE_MAX_LENGTH + 1),
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json)

    assert response.status_code == 422
    assert db.query(Question).count() == 0


def test_create_dataset_question_with_invalid_max_length_description(
    client: TestClient, db: Session, owner_auth_header
):
    dataset = DatasetFactory.create()
    question_json = {
        "name": "name",
        "title": "title",
        "description": "a" * (QUESTION_CREATE_DESCRIPTION_MAX_LENGTH + 1),
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json)

    assert response.status_code == 422
    assert db.query(Question).count() == 0


def test_create_dataset_question_with_existent_name(client: TestClient, db: Session, owner_auth_header):
    question = QuestionFactory.create(name="name")
    question_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(
        f"/api/v1/datasets/{question.dataset.id}/questions", headers=owner_auth_header, json=question_json
    )

    assert response.status_code == 409
    assert db.query(Question).count() == 1


def test_create_dataset_question_with_published_dataset(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    question_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Question cannot be created for a published dataset"}
    assert db.query(Question).count() == 0


def test_create_dataset_question_with_nonexistent_dataset_id(client: TestClient, db: Session, owner_auth_header):
    DatasetFactory.create()
    question_json = {
        "name": "text",
        "title": "Text",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{uuid4()}/questions", headers=owner_auth_header, json=question_json)

    assert response.status_code == 404
    assert db.query(Question).count() == 0


@pytest.mark.parametrize(
    "settings",
    [
        None,
        {},
        {"type": "wrong"},
        {"type": "text", "use_markdown": None},
        {"type": "text", "use_markdown": "wrong"},
        {
            "type": "rating",
            "options": [
                {"value": "A wrong value"},
                {"value": "B wrong value"},
                {"value": "C wrong value"},
                {"value": "D wrong value"},
            ],
        },
        {"type": "rating", "options": [{"value": value} for value in range(0, RATING_OPTIONS_MIN_ITEMS - 1)]},
        {"type": "rating", "options": [{"value": value} for value in range(0, RATING_OPTIONS_MAX_ITEMS + 1)]},
        {"type": "rating", "options": "invalid"},
        {"type": "rating", "options": [{"value": 0}, {"value": 1}, {"value": 1}]},
        {"type": "label_selection", "options": []},
        {"type": "label_selection", "options": [{"value": "just_one_label", "text": "Just one label"}]},
        {
            "type": "label_selection",
            "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
            "visible_options": 0,
        },
        {
            "type": "label_selection",
            "options": [{"value": "a", "text": "a"}, {"value": "b", "text": "b"}],
            "visible_options": -1,
        },
        {
            "type": "label_selection",
            "options": [{"value": "", "text": "a"}, {"value": "b", "text": "b"}],
        },
        {
            "type": "label_selection",
            "options": [
                {"value": "".join(["a" for _ in range(VALUE_TEXT_OPTION_VALUE_MAX_LENGTH + 1)]), "text": "a"},
                {"value": "b", "text": "b"},
            ],
        },
        {
            "type": "label_selection",
            "options": [{"value": "a", "text": ""}, {"value": "b", "text": "b"}],
        },
        {
            "type": "label_selection",
            "options": [
                {"value": "a", "text": "".join(["a" for _ in range(VALUE_TEXT_OPTION_TEXT_MAX_LENGTH + 1)])},
                {"value": "b", "text": "b"},
            ],
        },
        {
            "type": "label_selection",
            "options": [{"value": "a", "text": "a", "description": ""}, {"value": "b", "text": "b"}],
        },
        {
            "type": "label_selection",
            "options": [
                {
                    "value": "a",
                    "text": "a",
                    "description": "".join(["a" for _ in range(VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH + 1)]),
                },
                {"value": "b", "text": "b"},
            ],
        },
        {
            "type": "label_selection",
            "options": [
                {"value": "a", "text": "a", "description": "a"},
                {"value": "b", "text": "b", "description": "b"},
                {"value": "b", "text": "b", "description": "b"},
            ],
        },
        {
            "type": "ranking",
            "options": [
                {"value": "a", "text": "a", "description": "a"},
            ],
        },
        {
            "type": "ranking",
            "options": [
                {"value": "a", "text": "a", "description": "a"},
                {"value": "b", "text": "b", "description": "b"},
                {"value": "b", "text": "b", "description": "b"},
            ],
        },
        {
            "type": "ranking",
            "options": [
                {
                    "value": "a",
                    "text": "a",
                    "description": "".join(["a" for _ in range(VALUE_TEXT_OPTION_DESCRIPTION_MAX_LENGTH + 1)]),
                },
                {"value": "b", "text": "b", "description": "b"},
            ],
        },
    ],
)
def test_create_dataset_question_with_invalid_settings(
    client: TestClient,
    db: Session,
    owner_auth_header,
    settings: dict,
):
    dataset = DatasetFactory.create()
    question_json = {"name": "question", "title": "Question", "settings": settings}

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=owner_auth_header, json=question_json)

    assert response.status_code == 422
    assert db.query(Question).count() == 0


def test_create_dataset_records(
    client: TestClient,
    mock_search_engine: SearchEngine,
    test_telemetry: MagicMock,
    db: Session,
    owner,
    owner_auth_header,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)

    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": "Hello"},
                "external_id": "1",
                "responses": [
                    {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                        "status": "submitted",
                        "user_id": str(owner.id),
                    }
                ],
            },
            {
                "fields": {"input": "Say Hello", "output": "Hi"},
            },
            {
                "fields": {"input": "Say Pello", "output": "Hello World"},
                "external_id": "3",
                "responses": [
                    {
                        "values": {"input_ok": {"value": "no"}, "output_ok": {"value": "no"}},
                        "status": "submitted",
                        "user_id": str(owner.id),
                    }
                ],
            },
            {
                "fields": {"input": "Say Hello", "output": "Good Morning"},
                "responses": [
                    {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "no"}},
                        "status": "discarded",
                        "user_id": str(owner.id),
                    }
                ],
            },
            {
                "fields": {"input": "Say Hello", "output": "Say Hello"},
                "responses": [
                    {
                        "user_id": str(owner.id),
                        "status": "discarded",
                    }
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 204, response.json()
    assert db.query(Record).count() == 5
    assert db.query(Response).count() == 4

    mock_search_engine.add_records.assert_called_once_with(dataset, db.query(Record).all())

    test_telemetry.assert_called_once_with(action="DatasetRecordsCreated", data={"records": len(records_json["items"])})


def test_create_dataset_records_with_response_for_multiple_users(
    client: TestClient, mock_search_engine: SearchEngine, db: Session, owner, owner_auth_header
):
    workspace = WorkspaceFactory.create()

    dataset = DatasetFactory.create(status=DatasetStatus.ready, workspace=workspace)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    annotator = AnnotatorFactory.create(workspaces=[workspace])

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": "Hello"},
                "external_id": "1",
                "responses": [
                    {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                        "status": "submitted",
                        "user_id": str(owner.id),
                    },
                    {
                        "status": "discarded",
                        "user_id": str(annotator.id),
                    },
                ],
            },
            {
                "fields": {"input": "Say Pello", "output": "Hello World"},
                "external_id": "3",
                "responses": [
                    {
                        "values": {"input_ok": {"value": "no"}, "output_ok": {"value": "no"}},
                        "status": "submitted",
                        "user_id": str(annotator.id),
                    }
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 204, response.json()
    assert db.query(Record).count() == 2
    assert db.query(Response).filter(Response.user_id == annotator.id).count() == 2
    assert db.query(Response).filter(Response.user_id == owner.id).count() == 1

    mock_search_engine.add_records.assert_called_once_with(dataset, db.query(Record).all())


def test_create_dataset_records_with_response_for_unknown_user(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": "Hello"},
                "external_id": "1",
                "responses": [
                    {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                        "status": "submitted",
                        "user_id": str(uuid4()),
                    },
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 422, response.json()
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_duplicated_response_for_an_user(
    client: TestClient, db: Session, owner, owner_auth_header
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": "Hello"},
                "external_id": "1",
                "responses": [
                    {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                        "status": "submitted",
                        "user_id": str(owner.id),
                    },
                    {
                        "values": {"input_ok": {"value": "no"}, "output_ok": {"value": "no"}},
                        "status": "submitted",
                        "user_id": str(owner.id),
                    },
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 422, response.json()
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::ValidationError",
            "params": {
                "model": "Request",
                "errors": [
                    {
                        "loc": ["body", "items", 0, "responses"],
                        "msg": f"Responses contains several responses for the same user_id: {str(owner.id)!r}",
                        "type": "value_error",
                    }
                ],
            },
        }
    }
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_missing_required_fields(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    FieldFactory.create(name="input", dataset=dataset, required=True)
    FieldFactory.create(name="output", dataset=dataset, required=True)

    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello"},
            },
            {
                "fields": {"input": "Say Hello", "output": "Hi"},
            },
            {
                "fields": {"input": "Say Pello", "output": "Hello World"},
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Missing required value for field: 'output'"}
    assert db.query(Record).count() == 0


def test_create_dataset_records_with_wrong_value_field(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    FieldFactory.create(name="input", dataset=dataset)
    FieldFactory.create(name="output", dataset=dataset)

    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": 33},
            },
            {
                "fields": {"input": "Say Hello", "output": "Hi"},
            },
            {
                "fields": {"input": "Say Pello", "output": "Hello World"},
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Wrong value found for field 'output'. Expected 'str', found 'int'"}
    assert db.query(Record).count() == 0


def test_create_dataset_records_with_extra_fields(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    FieldFactory.create(name="input", dataset=dataset)

    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": "unexpected"},
            },
            {
                "fields": {"input": "Say Hello"},
            },
            {
                "fields": {"input": "Say Pello"},
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Error: found fields values for non configured fields: ['output']"}
    assert db.query(Record).count() == 0


def test_create_dataset_records_with_index_error(
    client: TestClient, mock_search_engine: SearchEngine, db: Session, owner_auth_header
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)

    records_json = {
        "items": [
            {"fields": {"input": "Say Hello", "output": "Hello"}},
            {"fields": {"input": "Say Hello", "output": "Hi"}},
            {"fields": {"input": "Say Pello", "output": "Hello World"}},
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 422
    assert db.query(Record).count() == 0

    assert not mock_search_engine.create_index.called


def test_create_dataset_records_without_authentication(client: TestClient, db: Session):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "ouput": "Hello"},
                "external_id": "1",
                "response": {
                    "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                    "status": "submitted",
                },
            },
        ],
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", json=records_json)

    assert response.status_code == 401
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_as_admin(client: TestClient, db: Session):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    admin = AdminFactory.create(workspaces=[dataset.workspace])

    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)

    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": "Hello"},
                "external_id": "1",
                "responses": [
                    {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                        "status": "submitted",
                        "user_id": str(admin.id),
                    }
                ],
            },
            {
                "fields": {"input": "Say Hello", "output": "Hi"},
            },
            {
                "fields": {"input": "Say Pello", "output": "Hello World"},
                "external_id": "3",
                "responses": [
                    {
                        "values": {"input_ok": {"value": "no"}, "output_ok": {"value": "no"}},
                        "status": "submitted",
                        "user_id": str(admin.id),
                    }
                ],
            },
            {
                "fields": {"input": "Say Hello", "output": "Good Morning"},
                "responses": [
                    {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "no"}},
                        "status": "discarded",
                        "user_id": str(admin.id),
                    }
                ],
            },
            {
                "fields": {"input": "Say Hello", "output": "Say Hello"},
                "responses": [
                    {
                        "user_id": str(admin.id),
                        "status": "discarded",
                    }
                ],
            },
        ]
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: admin.api_key}, json=records_json
    )

    assert response.status_code == 204
    assert db.query(Record).count() == 5
    assert db.query(Response).count() == 4


def test_create_dataset_records_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "ouput": "Hello"},
                "external_id": "1",
                "response": {
                    "values": {
                        "input_ok": {"value": "yes"},
                        "output_ok": {"value": "yes"},
                    },
                    "status": "submitted",
                },
            },
        ],
    }

    response = client.post(
        f"/api/v1/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=records_json
    )

    assert response.status_code == 403
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_submitted_response(client: TestClient, db: Session, owner, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)

    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": "Hello"},
                "responses": [
                    {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                        "status": "submitted",
                        "user_id": str(owner.id),
                    }
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 204
    assert db.query(Record).count() == 1
    assert db.query(Response).count() == 1


def test_create_dataset_records_with_submitted_response_without_values(
    client: TestClient,
    db: Session,
    owner,
    owner_auth_header,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "ouput": "Hello"},
                "responses": [
                    {
                        "user_id": str(owner.id),
                        "status": "submitted",
                    }
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 422
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_discarded_response(
    client: TestClient,
    db: Session,
    owner,
    owner_auth_header,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)

    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": "Hello"},
                "responses": [
                    {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                        "status": "discarded",
                        "user_id": str(owner.id),
                    }
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 204
    assert db.query(Record).count() == 1
    assert db.query(Response).filter(Response.status == ResponseStatus.discarded).count() == 1


def test_create_dataset_records_with_invalid_response_status(
    client: TestClient,
    db: Session,
    owner,
    owner_auth_header,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "ouput": "Hello"},
                "responses": [
                    {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                        "status": "invalid",
                        "user_id": str(owner.id),
                    }
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 422
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_discarded_response_without_values(
    client: TestClient,
    db: Session,
    owner,
    owner_auth_header,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)

    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": "Hello"},
                "responses": [
                    {
                        "status": "discarded",
                        "user_id": str(owner.id),
                    }
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 204
    assert db.query(Record).count() == 1
    assert db.query(Response).count() == 1


def test_create_dataset_records_with_non_published_dataset(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.draft)
    records_json = {
        "items": [
            {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": "1"},
        ],
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Records cannot be created for a non published dataset"}
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_less_items_than_allowed(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "ouput": "Hello"},
                "external_id": str(external_id),
            }
            for external_id in range(0, RECORDS_CREATE_MIN_ITEMS - 1)
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 422
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_more_items_than_allowed(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "ouput": "Hello"},
                "external_id": str(external_id),
            }
            for external_id in range(0, RECORDS_CREATE_MAX_ITEMS + 1)
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 422
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_invalid_records(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    records_json = {
        "items": [
            {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": 1},
            {"fields": "invalid", "external_id": 2},
            {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": 3},
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 422
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_nonexistent_dataset_id(client: TestClient, db: Session, owner_auth_header):
    DatasetFactory.create()
    records_json = {
        "items": [
            {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": 1},
            {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": 2},
        ]
    }

    response = client.post(f"/api/v1/datasets/{uuid4()}/records", headers=owner_auth_header, json=records_json)

    assert response.status_code == 404
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def create_dataset_for_search(user: Optional[User] = None) -> Tuple[Dataset, List[Record], List[Response]]:
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)
    records = [
        RecordFactory.create(dataset=dataset, fields={"input": "Say Hello", "output": "Hello"}),
        RecordFactory.create(dataset=dataset, metadata_={"unit": "test"}, fields={"input": "Hello", "output": "Hi"}),
        RecordFactory.create(dataset=dataset, fields={"input": "Say Goodbye", "output": "Goodbye"}),
        RecordFactory.create(dataset=dataset, fields={"input": "Say bye", "output": "Bye"}),
    ]
    responses = [
        ResponseFactory.create(
            record=records[0],
            values={"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
            status=ResponseStatus.submitted,
            user=user,
        ),
        ResponseFactory.create(
            record=records[1],
            values={"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
            status=ResponseStatus.submitted,
            user=user,
        ),
        ResponseFactory.create(
            record=records[2],
            values={"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
            status=ResponseStatus.submitted,
            user=user,
        ),
        ResponseFactory.create(
            record=records[3],
            values={"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
            status=ResponseStatus.submitted,
            user=user,
        ),
    ]
    # Add some responses from other users
    ResponseFactory.create_batch(10, record=records[0], status=ResponseStatus.submitted)
    return dataset, records, responses


def test_search_dataset_records(client: TestClient, mock_search_engine: SearchEngine, owner, owner_auth_header):
    dataset, records, _ = create_dataset_for_search(user=owner)

    mock_search_engine.search.return_value = SearchResponses(
        items=[
            SearchResponseItem(record_id=records[0].id, score=14.2),
            SearchResponseItem(record_id=records[1].id, score=12.2),
        ],
        total=2,
    )

    query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}
    response = client.post(
        f"/api/v1/me/datasets/{dataset.id}/records/search", headers=owner_auth_header, json=query_json
    )

    mock_search_engine.search.assert_called_once_with(
        dataset=dataset,
        query=Query(
            text=TextQuery(
                q="Hello",
                field="input",
            )
        ),
        user_response_status_filter=None,
        offset=0,
        limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
    )
    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "record": {
                    "id": str(records[0].id),
                    "fields": {
                        "input": "Say Hello",
                        "output": "Hello",
                    },
                    "metadata": None,
                    "external_id": records[0].external_id,
                    "inserted_at": records[0].inserted_at.isoformat(),
                    "updated_at": records[0].updated_at.isoformat(),
                },
                "query_score": 14.2,
            },
            {
                "record": {
                    "id": str(records[1].id),
                    "fields": {
                        "input": "Hello",
                        "output": "Hi",
                    },
                    "metadata": {"unit": "test"},
                    "external_id": records[1].external_id,
                    "inserted_at": records[1].inserted_at.isoformat(),
                    "updated_at": records[1].updated_at.isoformat(),
                },
                "query_score": 12.2,
            },
        ],
        "total": 2,
    }


def test_search_dataset_records_including_responses(
    client: TestClient, mock_search_engine: SearchEngine, owner, owner_auth_header
):
    dataset, records, responses = create_dataset_for_search(user=owner)

    mock_search_engine.search.return_value = SearchResponses(
        items=[
            SearchResponseItem(record_id=records[0].id, score=14.2),
            SearchResponseItem(record_id=records[1].id, score=12.2),
        ],
        total=2,
    )

    query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}
    response = client.post(
        f"/api/v1/me/datasets/{dataset.id}/records/search",
        headers=owner_auth_header,
        json=query_json,
        params={"include": RecordInclude.responses.value},
    )

    mock_search_engine.search.assert_called_once_with(
        dataset=dataset,
        query=Query(
            text=TextQuery(
                q="Hello",
                field="input",
            )
        ),
        user_response_status_filter=None,
        offset=0,
        limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
    )
    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "record": {
                    "id": str(records[0].id),
                    "fields": {
                        "input": "Say Hello",
                        "output": "Hello",
                    },
                    "metadata": None,
                    "external_id": records[0].external_id,
                    "responses": [
                        {
                            "id": str(responses[0].id),
                            "values": {
                                "input_ok": {"value": "yes"},
                                "output_ok": {"value": "yes"},
                            },
                            "status": "submitted",
                            "user_id": str(responses[0].user_id),
                            "inserted_at": responses[0].inserted_at.isoformat(),
                            "updated_at": responses[0].updated_at.isoformat(),
                        }
                    ],
                    "inserted_at": records[0].inserted_at.isoformat(),
                    "updated_at": records[0].updated_at.isoformat(),
                },
                "query_score": 14.2,
            },
            {
                "record": {
                    "id": str(records[1].id),
                    "fields": {
                        "input": "Hello",
                        "output": "Hi",
                    },
                    "metadata": {"unit": "test"},
                    "external_id": records[1].external_id,
                    "responses": [
                        {
                            "id": str(responses[1].id),
                            "values": {
                                "input_ok": {"value": "yes"},
                                "output_ok": {"value": "yes"},
                            },
                            "status": "submitted",
                            "user_id": str(responses[1].user_id),
                            "inserted_at": responses[1].inserted_at.isoformat(),
                            "updated_at": responses[1].updated_at.isoformat(),
                        }
                    ],
                    "inserted_at": records[1].inserted_at.isoformat(),
                    "updated_at": records[1].updated_at.isoformat(),
                },
                "query_score": 12.2,
            },
        ],
        "total": 2,
    }


def test_search_dataset_records_with_response_status_filter(
    client: TestClient, mock_search_engine: SearchEngine, owner, owner_auth_header
):
    dataset, _, _ = create_dataset_for_search(user=owner)
    mock_search_engine.search.return_value = SearchResponses(items=[], total=0)

    query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}
    response = client.post(
        f"/api/v1/me/datasets/{dataset.id}/records/search",
        headers=owner_auth_header,
        json=query_json,
        params={"response_status": ResponseStatus.submitted.value},
    )

    mock_search_engine.search.assert_called_once_with(
        dataset=dataset,
        query=Query(text=TextQuery(q="Hello", field="input")),
        user_response_status_filter=UserResponseStatusFilter(user=owner, status=ResponseStatus.submitted),
        offset=0,
        limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
    )
    assert response.status_code == 200


def test_search_dataset_records_with_offset_and_limit(
    client: TestClient, mock_search_engine: SearchEngine, owner, owner_auth_header
):
    dataset, records, _ = create_dataset_for_search(user=owner)
    mock_search_engine.search.return_value = SearchResponses(
        items=[
            SearchResponseItem(record_id=records[0].id, score=14.2),
            SearchResponseItem(record_id=records[1].id, score=12.2),
        ],
        total=2,
    )

    query_json = {"query": {"text": {"q": "Hello", "field": "input"}}}
    response = client.post(
        f"/api/v1/me/datasets/{dataset.id}/records/search",
        headers=owner_auth_header,
        json=query_json,
        params={"offset": 0, "limit": 5},
    )

    mock_search_engine.search.assert_called_once_with(
        dataset=dataset,
        query=Query(text=TextQuery(q="Hello", field="input")),
        user_response_status_filter=None,
        offset=0,
        limit=5,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json["items"]) == 2
    assert response_json["total"] == 2


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
def test_search_dataset_records_as_restricted_user(
    client: TestClient, owner: User, mock_search_engine: SearchEngine, role: UserRole
):
    dataset, records, _ = create_dataset_for_search(user=owner)
    user = UserFactory.create(workspaces=[dataset.workspace], role=role)

    mock_search_engine.search.return_value = SearchResponses(
        items=[
            SearchResponseItem(record_id=records[0].id, score=14.2),
            SearchResponseItem(record_id=records[1].id, score=12.2),
        ],
        total=2,
    )

    query_json = {"query": {"text": {"q": "unit test", "field": "input"}}}
    response = client.post(
        f"/api/v1/me/datasets/{dataset.id}/records/search",
        headers={API_KEY_HEADER_NAME: user.api_key},
        json=query_json,
    )

    mock_search_engine.search.assert_called_once_with(
        dataset=dataset,
        query=Query(
            text=TextQuery(
                q="unit test",
                field="input",
            )
        ),
        user_response_status_filter=None,
        offset=0,
        limit=LIST_DATASET_RECORDS_LIMIT_DEFAULT,
    )
    assert response.status_code == 200


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.annotator])
def test_search_dataset_records_as_restricted_user_from_different_workspace(client: TestClient, role: UserRole):
    dataset, _, _ = create_dataset_for_search()
    user = UserFactory.create(workspaces=[WorkspaceFactory.create()], role=role)

    query_json = {"query": {"text": {"q": "unit test", "field": "input"}}}
    response = client.post(
        f"/api/v1/me/datasets/{dataset.id}/records/search",
        headers={API_KEY_HEADER_NAME: user.api_key},
        json=query_json,
    )

    assert response.status_code == 403


def test_search_dataset_records_with_non_existent_field(client: TestClient, owner_auth_header):
    dataset, _, _ = create_dataset_for_search()

    query_json = {"query": {"text": {"q": "unit test", "field": "i do not exist"}}}
    response = client.post(
        f"/api/v1/me/datasets/{dataset.id}/records/search", headers=owner_auth_header, json=query_json
    )

    assert response.status_code == 422


def test_search_dataset_with_non_existent_dataset(client: TestClient, owner_auth_header):
    query_json = {"query": {"text": {"q": "unit test", "field": "input"}}}
    response = client.post(f"/api/v1/me/datasets/{uuid4()}/records/search", headers=owner_auth_header, json=query_json)

    assert response.status_code == 404


@pytest.mark.asyncio
def test_publish_dataset(
    client: TestClient,
    db: Session,
    mock_search_engine: SearchEngine,
    test_telemetry: MagicMock,
    owner_auth_header,
):
    dataset = DatasetFactory.create()
    TextFieldFactory.create(dataset=dataset)
    RatingQuestionFactory.create(dataset=dataset)

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=owner_auth_header)

    assert response.status_code == 200
    assert db.get(Dataset, dataset.id).status == "ready"

    response_body = response.json()
    assert response_body["status"] == "ready"

    test_telemetry.assert_called_once_with(action="PublishedDataset", data={"questions": ["rating"]})
    mock_search_engine.create_index.assert_called_once_with(dataset)


def test_publish_dataset_with_error_on_index_creation(
    client: TestClient, db: Session, mock_search_engine: SearchEngine, mocker, owner_auth_header
):
    mocker.patch.object(mock_search_engine, "create_index", side_effect=ValueError("Error creating index"))

    dataset = DatasetFactory.create()
    TextFieldFactory.create(dataset=dataset)
    QuestionFactory.create(settings={"type": "invalid"}, dataset=dataset)

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=owner_auth_header)

    assert response.status_code == 422
    assert db.get(Dataset, dataset.id).status == "draft"


def test_publish_dataset_without_authentication(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    QuestionFactory.create(dataset=dataset)

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish")

    assert response.status_code == 401
    assert db.get(Dataset, dataset.id).status == "draft"


def test_publish_dataset_as_admin(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    TextFieldFactory.create(dataset=dataset)
    RatingQuestionFactory.create(dataset=dataset)
    admin = AdminFactory.create(workspaces=[dataset.workspace])

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers={API_KEY_HEADER_NAME: admin.api_key})

    assert response.status_code == 200
    assert db.get(Dataset, dataset.id).status == "ready"

    response_body = response.json()
    assert response_body["status"] == "ready"


def test_publish_dataset_as_annotator(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    QuestionFactory.create(dataset=dataset)
    annotator = AnnotatorFactory.create(workspaces=[dataset.workspace])

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403
    assert db.get(Dataset, dataset.id).status == "draft"


def test_publish_dataset_already_published(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    QuestionFactory.create(dataset=dataset)

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=owner_auth_header)

    assert response.status_code == 422
    assert response.json() == {"detail": "Dataset is already published"}
    assert db.get(Dataset, dataset.id).status == "ready"


def test_publish_dataset_without_fields(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create()
    RatingQuestionFactory.create(dataset=dataset)

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=owner_auth_header)

    assert response.status_code == 422
    assert response.json() == {"detail": "Dataset cannot be published without fields"}
    assert db.get(Dataset, dataset.id).status == "draft"


def test_publish_dataset_without_questions(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create()
    TextFieldFactory.create(dataset=dataset)

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=owner_auth_header)

    assert response.status_code == 422
    assert response.json() == {"detail": "Dataset cannot be published without questions"}
    assert db.get(Dataset, dataset.id).status == "draft"


def test_publish_dataset_with_nonexistent_dataset_id(client: TestClient, db: Session, owner_auth_header):
    dataset = DatasetFactory.create()
    QuestionFactory.create(dataset=dataset)

    response = client.put(f"/api/v1/datasets/{uuid4()}/publish", headers=owner_auth_header)

    assert response.status_code == 404
    assert db.get(Dataset, dataset.id).status == "draft"


def test_delete_dataset(client: TestClient, db: Session, mock_search_engine: SearchEngine, owner, owner_auth_header):
    dataset = DatasetFactory.create()
    TextFieldFactory.create(dataset=dataset)
    TextQuestionFactory.create(dataset=dataset)

    other_dataset = DatasetFactory.create()
    other_field = TextFieldFactory.create(dataset=other_dataset)
    other_question = TextQuestionFactory.create(dataset=other_dataset)
    other_record = RecordFactory.create(dataset=other_dataset)
    other_response = ResponseFactory.create(record=other_record, user=owner)

    response = client.delete(f"/api/v1/datasets/{dataset.id}", headers=owner_auth_header)

    assert response.status_code == 200
    assert [dataset.id for dataset in db.query(Dataset).all()] == [other_dataset.id]
    assert [field.id for field in db.query(Field).all()] == [other_field.id]
    assert [question.id for question in db.query(Question).all()] == [other_question.id]
    assert [record.id for record in db.query(Record).all()] == [other_record.id]
    assert [response.id for response in db.query(Response).all()] == [other_response.id]
    assert [workspace.id for workspace in db.query(Workspace).order_by(Workspace.inserted_at.asc()).all()] == [
        dataset.workspace_id,
        other_dataset.workspace_id,
    ]

    mock_search_engine.delete_index.assert_called_once_with(dataset)


def test_delete_published_dataset(client: TestClient, db: Session, owner, owner_auth_header):
    dataset = DatasetFactory.create()
    TextFieldFactory.create(dataset=dataset)
    TextQuestionFactory.create(dataset=dataset)
    record = RecordFactory.create(dataset=dataset)
    ResponseFactory.create(record=record, user=owner)

    other_dataset = DatasetFactory.create()
    other_field = TextFieldFactory.create(dataset=other_dataset)
    other_question = TextQuestionFactory.create(dataset=other_dataset)
    other_record = RecordFactory.create(dataset=other_dataset)
    other_response = ResponseFactory.create(record=other_record, user=owner)

    response = client.delete(f"/api/v1/datasets/{dataset.id}", headers=owner_auth_header)

    assert response.status_code == 200
    assert [dataset.id for dataset in db.query(Dataset).all()] == [other_dataset.id]
    assert [field.id for field in db.query(Field).all()] == [other_field.id]
    assert [question.id for question in db.query(Question).all()] == [other_question.id]
    assert [record.id for record in db.query(Record).all()] == [other_record.id]
    assert [response.id for response in db.query(Response).all()] == [other_response.id]
    assert [workspace.id for workspace in db.query(Workspace).order_by(Workspace.inserted_at.asc()).all()] == [
        dataset.workspace_id,
        other_dataset.workspace_id,
    ]


def test_delete_dataset_without_authentication(client: TestClient, db: Session, mock_search_engine: SearchEngine):
    dataset = DatasetFactory.create()

    response = client.delete(f"/api/v1/datasets/{dataset.id}")

    assert response.status_code == 401
    assert db.query(Dataset).count() == 1

    assert not mock_search_engine.delete_index.called


def test_delete_dataset_as_admin(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    admin = AdminFactory.create(workspaces=[dataset.workspace])

    response = client.delete(f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: admin.api_key})

    assert response.status_code == 200
    assert db.query(Dataset).count() == 0


def test_delete_dataset_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    dataset = DatasetFactory.create()

    response = client.delete(f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403
    assert db.query(Dataset).count() == 1


def test_delete_dataset_with_nonexistent_dataset_id(client: TestClient, db: Session, owner_auth_header):
    DatasetFactory.create()

    response = client.delete(f"/api/v1/datasets/{uuid4()}", headers=owner_auth_header)

    assert response.status_code == 404
    assert db.query(Dataset).count() == 1
