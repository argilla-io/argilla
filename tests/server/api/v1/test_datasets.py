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
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from argilla._constants import API_KEY_HEADER_NAME
from argilla.server.models import (
    Dataset,
    DatasetStatus,
    Field,
    Question,
    Record,
    Response,
    ResponseStatus,
    User,
    Workspace,
)
from argilla.server.schemas.v1.datasets import (
    DATASET_CREATE_GUIDELINES_MAX_LENGTH,
    FIELD_CREATE_NAME_MAX_LENGTH,
    FIELD_CREATE_TITLE_MAX_LENGTH,
    LABEL_SELECTION_DESCRIPTION_MAX_LENGTH,
    LABEL_SELECTION_TEXT_MAX_LENGTH,
    LABEL_SELECTION_VALUE_MAX_LENGHT,
    QUESTION_CREATE_DESCRIPTION_MAX_LENGTH,
    QUESTION_CREATE_NAME_MAX_LENGTH,
    QUESTION_CREATE_TITLE_MAX_LENGTH,
    RATING_OPTIONS_MAX_ITEMS,
    RATING_OPTIONS_MIN_ITEMS,
    RECORDS_CREATE_MAX_ITEMS,
    RECORDS_CREATE_MIN_ITEMS,
    RecordInclude,
)
from argilla.server.search_engine import SearchEngine
from fastapi.testclient import TestClient
from opensearchpy import OpenSearch
from sqlalchemy.orm import Session

from tests.factories import (
    AnnotatorFactory,
    DatasetFactory,
    FieldFactory,
    QuestionFactory,
    RatingQuestionFactory,
    RecordFactory,
    ResponseFactory,
    TextFieldFactory,
    TextQuestionFactory,
    WorkspaceFactory,
)


def test_list_current_user_datasets(client: TestClient, admin_auth_header: dict):
    dataset_a = DatasetFactory.create(name="dataset-a")
    dataset_b = DatasetFactory.create(name="dataset-b", guidelines="guidelines")
    dataset_c = DatasetFactory.create(name="dataset-c", status=DatasetStatus.ready)

    response = client.get("/api/v1/me/datasets", headers=admin_auth_header)

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


def test_list_current_user_datasets_as_annotator(client: TestClient):
    workspace = WorkspaceFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[workspace])

    DatasetFactory.create(name="dataset-a", workspace=workspace)
    DatasetFactory.create(name="dataset-b", workspace=workspace)
    DatasetFactory.create(name="dataset-c")

    response = client.get("/api/v1/me/datasets", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200

    response_body = response.json()
    assert [dataset["name"] for dataset in response_body["items"]] == ["dataset-a", "dataset-b"]


def test_list_dataset_fields(client: TestClient, admin_auth_header: dict):
    dataset = DatasetFactory.build()
    text_field_a = TextFieldFactory.create(name="text-field-a", title="Text Field A", required=True, dataset=dataset)
    text_field_b = TextFieldFactory.create(name="text-field-b", title="Text Field B", dataset=dataset)

    other_dataset = DatasetFactory.create()
    TextFieldFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/datasets/{dataset.id}/fields", headers=admin_auth_header)

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


def test_list_dataset_fields_as_annotator(client: TestClient):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[dataset.workspace])
    TextFieldFactory.create(name="text-field-a", dataset=dataset)
    TextFieldFactory.create(name="text-field-b", dataset=dataset)

    other_dataset = DatasetFactory.create()
    TextFieldFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/datasets/{dataset.id}/fields", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200

    response_body = response.json()
    assert [field["name"] for field in response_body["items"]] == ["text-field-a", "text-field-b"]


def test_list_dataset_fields_as_annotator_from_different_workspace(client: TestClient):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[WorkspaceFactory.build()])

    response = client.get(f"/api/v1/datasets/{dataset.id}/fields", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403


def test_list_dataset_fields_with_nonexistent_dataset_id(client: TestClient, admin_auth_header: dict):
    DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{uuid4()}/fields", headers=admin_auth_header)

    assert response.status_code == 404


def test_list_dataset_questions(client: TestClient, admin_auth_header: dict):
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

    response = client.get(f"/api/v1/datasets/{dataset.id}/questions", headers=admin_auth_header)

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


def test_list_dataset_questions_without_authentication(client: TestClient):
    dataset = DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{dataset.id}/questions")

    assert response.status_code == 401


def test_list_dataset_questions_as_annotator(client: TestClient):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[dataset.workspace])
    TextQuestionFactory.create(name="text-question", dataset=dataset)
    RatingQuestionFactory.create(name="rating-question", dataset=dataset)
    TextQuestionFactory.create()
    RatingQuestionFactory.create()

    response = client.get(f"/api/v1/datasets/{dataset.id}/questions", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200

    response_body = response.json()
    assert [question["name"] for question in response_body["items"]] == ["text-question", "rating-question"]


def test_list_dataset_questions_as_annotator_from_different_workspace(client: TestClient):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[WorkspaceFactory.build()])

    response = client.get(f"/api/v1/datasets/{dataset.id}/questions", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403


def test_list_dataset_questions_with_nonexistent_dataset_id(client: TestClient, admin_auth_header: dict):
    DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{uuid4()}/questions", headers=admin_auth_header)

    assert response.status_code == 404


def test_list_dataset_records(client: TestClient, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_b = RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(record_a.id),
                "fields": {"record_a": "value_a"},
                "external_id": record_a.external_id,
                "inserted_at": record_a.inserted_at.isoformat(),
                "updated_at": record_a.updated_at.isoformat(),
            },
            {
                "id": str(record_b.id),
                "fields": {"record_b": "value_b"},
                "external_id": record_b.external_id,
                "inserted_at": record_b.inserted_at.isoformat(),
                "updated_at": record_b.updated_at.isoformat(),
            },
            {
                "id": str(record_c.id),
                "fields": {"record_c": "value_c"},
                "external_id": record_c.external_id,
                "inserted_at": record_c.inserted_at.isoformat(),
                "updated_at": record_c.updated_at.isoformat(),
            },
        ],
    }


def test_list_dataset_records_with_include_responses(client: TestClient, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_b = RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
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
        headers=admin_auth_header,
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(record_a.id),
                "fields": {"record_a": "value_a"},
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
                "external_id": record_c.external_id,
                "responses": [],
                "inserted_at": record_c.inserted_at.isoformat(),
                "updated_at": record_c.updated_at.isoformat(),
            },
        ],
    }


def test_list_dataset_records_with_offset(client: TestClient, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, params={"offset": 2})

    assert response.status_code == 200

    response_body = response.json()
    assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]


def test_list_dataset_records_with_limit(client: TestClient, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, params={"limit": 1})

    assert response.status_code == 200

    response_body = response.json()
    assert [item["id"] for item in response_body["items"]] == [str(record_a.id)]


def test_list_dataset_records_with_offset_and_limit(client: TestClient, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(
        f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, params={"offset": 1, "limit": 1}
    )

    assert response.status_code == 200

    response_body = response.json()
    assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]


def test_list_dataset_records_without_authentication(client: TestClient):
    dataset = DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{dataset.id}/records")

    assert response.status_code == 401


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


def test_list_current_user_dataset_records(client: TestClient, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_b = RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/records", headers=admin_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(record_a.id),
                "fields": {"record_a": "value_a"},
                "external_id": record_a.external_id,
                "inserted_at": record_a.inserted_at.isoformat(),
                "updated_at": record_a.updated_at.isoformat(),
            },
            {
                "id": str(record_b.id),
                "fields": {"record_b": "value_b"},
                "external_id": record_b.external_id,
                "inserted_at": record_b.inserted_at.isoformat(),
                "updated_at": record_b.updated_at.isoformat(),
            },
            {
                "id": str(record_c.id),
                "fields": {"record_c": "value_c"},
                "external_id": record_c.external_id,
                "inserted_at": record_c.inserted_at.isoformat(),
                "updated_at": record_c.updated_at.isoformat(),
            },
        ],
    }


def test_list_current_user_dataset_records_with_include_responses(
    client: TestClient, admin: User, admin_auth_header: dict
):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[dataset.workspace])
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_b = RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    response_a_annotator = ResponseFactory.create(
        values={
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        record=record_a,
        user=annotator,
    )
    response_a_admin = ResponseFactory.create(
        status="discarded",
        record=record_a,
        user=admin,
    )
    response_b_annotator = ResponseFactory.create(
        values={
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "no"},
        },
        record=record_b,
        user=annotator,
    )
    response_b_admin = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        record=record_b,
        user=admin,
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
        headers=admin_auth_header,
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(record_a.id),
                "fields": {"record_a": "value_a"},
                "external_id": record_a.external_id,
                "responses": [
                    {
                        "id": str(response_a_admin.id),
                        "values": None,
                        "status": "discarded",
                        "user_id": str(admin.id),
                        "inserted_at": response_a_admin.inserted_at.isoformat(),
                        "updated_at": response_a_admin.updated_at.isoformat(),
                    }
                ],
                "inserted_at": record_a.inserted_at.isoformat(),
                "updated_at": record_a.updated_at.isoformat(),
            },
            {
                "id": str(record_b.id),
                "fields": {"record_b": "value_b"},
                "external_id": record_b.external_id,
                "responses": [
                    {
                        "id": str(response_b_admin.id),
                        "values": {
                            "input_ok": {"value": "no"},
                            "output_ok": {"value": "no"},
                        },
                        "status": "submitted",
                        "user_id": str(admin.id),
                        "inserted_at": response_b_admin.inserted_at.isoformat(),
                        "updated_at": response_b_admin.updated_at.isoformat(),
                    },
                ],
                "inserted_at": record_b.inserted_at.isoformat(),
                "updated_at": record_b.updated_at.isoformat(),
            },
            {
                "id": str(record_c.id),
                "fields": {"record_c": "value_c"},
                "external_id": record_c.external_id,
                "responses": [],
                "inserted_at": record_c.inserted_at.isoformat(),
                "updated_at": record_c.updated_at.isoformat(),
            },
        ],
    }


def test_list_current_user_dataset_records_with_offset(client: TestClient, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/records", headers=admin_auth_header, params={"offset": 2})

    assert response.status_code == 200

    response_body = response.json()
    assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]


def test_list_current_user_dataset_records_with_limit(client: TestClient, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/records", headers=admin_auth_header, params={"limit": 1})

    assert response.status_code == 200

    response_body = response.json()
    assert [item["id"] for item in response_body["items"]] == [str(record_a.id)]


def test_list_current_user_dataset_records_with_offset_and_limit(client: TestClient, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(
        f"/api/v1/me/datasets/{dataset.id}/records", headers=admin_auth_header, params={"offset": 1, "limit": 1}
    )

    assert response.status_code == 200

    response_body = response.json()
    assert [item["id"] for item in response_body["items"]] == [str(record_c.id)]


@pytest.mark.parametrize("response_status_filter", ["missing", "discarded", "submitted"])
def test_list_current_user_dataset_records_with_response_status_filter(
    client: TestClient, admin: User, admin_auth_header: dict, response_status_filter: str
):
    dataset = DatasetFactory.create()
    num_responses_per_status = 10
    # missing responses
    RecordFactory.create_batch(size=num_responses_per_status, dataset=dataset)
    # discarded responses
    for record in RecordFactory.create_batch(size=num_responses_per_status, dataset=dataset):
        ResponseFactory.create(record=record, user=admin, status=ResponseStatus.discarded)
    # submitted responses
    for record in RecordFactory.create_batch(size=num_responses_per_status, dataset=dataset):
        ResponseFactory.create(
            record=record,
            user=admin,
            values={
                "input_ok": {"value": "yes"},
                "output_ok": {"value": "yes"},
            },
            status=ResponseStatus.submitted,
        )

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(
        f"/api/v1/me/datasets/{dataset.id}/records?response_status={response_status_filter}&include=responses",
        headers=admin_auth_header,
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


def test_list_current_user_dataset_records_as_annotator(client: TestClient, admin: User):
    workspace = WorkspaceFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[workspace])
    dataset = DatasetFactory.create(workspace=workspace)
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_b = RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    other_dataset = DatasetFactory.create()
    RecordFactory.create_batch(size=2, dataset=other_dataset)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(record_a.id),
                "fields": {"record_a": "value_a"},
                "external_id": record_a.external_id,
                "inserted_at": record_a.inserted_at.isoformat(),
                "updated_at": record_a.updated_at.isoformat(),
            },
            {
                "id": str(record_b.id),
                "fields": {"record_b": "value_b"},
                "external_id": record_b.external_id,
                "inserted_at": record_b.inserted_at.isoformat(),
                "updated_at": record_b.updated_at.isoformat(),
            },
            {
                "id": str(record_c.id),
                "fields": {"record_c": "value_c"},
                "external_id": record_c.external_id,
                "inserted_at": record_c.inserted_at.isoformat(),
                "updated_at": record_c.updated_at.isoformat(),
            },
        ],
    }


def test_list_current_user_dataset_records_as_annotator_with_include_responses(client: TestClient, admin: User):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[dataset.workspace])
    record_a = RecordFactory.create(fields={"record_a": "value_a"}, dataset=dataset)
    record_b = RecordFactory.create(fields={"record_b": "value_b"}, dataset=dataset)
    record_c = RecordFactory.create(fields={"record_c": "value_c"}, dataset=dataset)

    response_a_admin = ResponseFactory.create(
        values={
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "yes"},
        },
        record=record_a,
        user=admin,
    )
    response_a_annotator = ResponseFactory.create(
        status="discarded",
        record=record_a,
        user=annotator,
    )
    response_b_admin = ResponseFactory.create(
        values={
            "input_ok": {"value": "yes"},
            "output_ok": {"value": "no"},
        },
        record=record_b,
        user=admin,
    )
    response_b_annotator = ResponseFactory.create(
        values={
            "input_ok": {"value": "no"},
            "output_ok": {"value": "no"},
        },
        record=record_b,
        user=annotator,
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
        headers={API_KEY_HEADER_NAME: annotator.api_key},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(record_a.id),
                "fields": {"record_a": "value_a"},
                "external_id": record_a.external_id,
                "responses": [
                    {
                        "id": str(response_a_annotator.id),
                        "values": None,
                        "status": "discarded",
                        "user_id": str(annotator.id),
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
                "external_id": record_b.external_id,
                "responses": [
                    {
                        "id": str(response_b_annotator.id),
                        "values": {
                            "input_ok": {"value": "no"},
                            "output_ok": {"value": "no"},
                        },
                        "status": "submitted",
                        "user_id": str(annotator.id),
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
                "external_id": record_c.external_id,
                "responses": [],
                "inserted_at": record_c.inserted_at.isoformat(),
                "updated_at": record_c.updated_at.isoformat(),
            },
        ],
    }


def test_list_current_user_dataset_records_as_annotator_from_different_workspace(client: TestClient):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[WorkspaceFactory.build()])

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/records", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403


def test_list_current_user_dataset_records_with_nonexistent_dataset_id(client: TestClient, admin_auth_header: dict):
    DatasetFactory.create()

    response = client.get(f"/api/v1/me/datasets/{uuid4()}/records", headers=admin_auth_header)

    assert response.status_code == 404


def test_get_dataset(client: TestClient, admin_auth_header: dict):
    dataset = DatasetFactory.create(name="dataset")

    response = client.get(f"/api/v1/datasets/{dataset.id}", headers=admin_auth_header)

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


def test_get_dataset_as_annotator(client: TestClient):
    dataset = DatasetFactory.create(name="dataset")
    annotator = AnnotatorFactory.create(workspaces=[dataset.workspace])

    response = client.get(f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200
    assert response.json()["name"] == "dataset"


def test_get_dataset_as_annotator_from_different_workspace(client: TestClient):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[WorkspaceFactory.build()])

    response = client.get(f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403


def test_get_dataset_with_nonexistent_dataset_id(client: TestClient, admin_auth_header: dict):
    DatasetFactory.create()

    response = client.get(f"/api/v1/datasets/{uuid4()}", headers=admin_auth_header)

    assert response.status_code == 404


def test_get_current_user_dataset_metrics(client: TestClient, admin: User, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    record_a = RecordFactory.create(dataset=dataset)
    record_b = RecordFactory.create(dataset=dataset)
    record_c = RecordFactory.create(dataset=dataset)
    RecordFactory.create_batch(3, dataset=dataset)
    ResponseFactory.create(record=record_a, user=admin)
    ResponseFactory.create(record=record_b, user=admin, status=ResponseStatus.discarded)
    ResponseFactory.create(record=record_c, user=admin, status=ResponseStatus.discarded)

    other_dataset = DatasetFactory.create()
    other_record_a = RecordFactory.create(dataset=other_dataset)
    other_record_b = RecordFactory.create(dataset=other_dataset)
    other_record_c = RecordFactory.create(dataset=other_dataset)
    RecordFactory.create_batch(2, dataset=other_dataset)
    ResponseFactory.create(record=other_record_a, user=admin)
    ResponseFactory.create(record=other_record_b)
    ResponseFactory.create(record=other_record_c, status=ResponseStatus.discarded)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/metrics", headers=admin_auth_header)

    assert response.status_code == 200
    assert response.json() == {
        "records": {
            "count": 6,
        },
        "responses": {
            "count": 3,
            "submitted": 1,
            "discarded": 2,
        },
    }


def test_get_current_user_dataset_metrics_without_authentication(client: TestClient):
    dataset = DatasetFactory.create()

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/metrics")

    assert response.status_code == 401


def test_get_current_user_dataset_metrics_as_annotator(client: TestClient):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[dataset.workspace])
    record_a = RecordFactory.create(dataset=dataset)
    record_b = RecordFactory.create(dataset=dataset)
    record_c = RecordFactory.create(dataset=dataset)
    RecordFactory.create_batch(2, dataset=dataset)
    ResponseFactory.create(record=record_a, user=annotator)
    ResponseFactory.create(record=record_b, user=annotator)
    ResponseFactory.create(record=record_c, user=annotator, status=ResponseStatus.discarded)

    other_dataset = DatasetFactory.create()
    other_record_a = RecordFactory.create(dataset=other_dataset)
    other_record_b = RecordFactory.create(dataset=other_dataset)
    other_record_c = RecordFactory.create(dataset=other_dataset)
    RecordFactory.create_batch(3, dataset=other_dataset)
    ResponseFactory.create(record=other_record_a, user=annotator)
    ResponseFactory.create(record=other_record_b)
    ResponseFactory.create(record=other_record_c, status=ResponseStatus.discarded)

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/metrics", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 200
    assert response.json() == {
        "records": {
            "count": 5,
        },
        "responses": {
            "count": 3,
            "submitted": 2,
            "discarded": 1,
        },
    }


def test_get_current_user_dataset_metrics_annotator_from_different_workspace(client: TestClient):
    dataset = DatasetFactory.create()
    annotator = AnnotatorFactory.create(workspaces=[WorkspaceFactory.build()])

    response = client.get(f"/api/v1/me/datasets/{dataset.id}/metrics", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403


def test_get_current_user_dataset_metrics_with_nonexistent_dataset_id(client: TestClient, admin_auth_header: dict):
    DatasetFactory.create()

    response = client.get(f"/api/v1/me/datasets/{uuid4()}/metrics", headers=admin_auth_header)

    assert response.status_code == 404


def test_create_dataset(client: TestClient, db: Session, admin_auth_header: dict):
    workspace = WorkspaceFactory.create()
    dataset_json = {"name": "name", "guidelines": "guidelines", "workspace_id": str(workspace.id)}

    response = client.post("/api/v1/datasets", headers=admin_auth_header, json=dataset_json)

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


def test_create_dataset_with_invalid_length_guidelines(client: TestClient, db: Session, admin_auth_header: dict):
    workspace = WorkspaceFactory.create()
    dataset_json = {
        "name": "name",
        "guidelines": "a" * (DATASET_CREATE_GUIDELINES_MAX_LENGTH + 1),
        "workspace_id": str(workspace.id),
    }

    response = client.post("/api/v1/datasets", headers=admin_auth_header, json=dataset_json)

    assert response.status_code == 422
    assert db.query(Dataset).count() == 0


def test_create_dataset_without_authentication(client: TestClient, db: Session):
    dataset_json = {"name": "name", "workspace_id": str(WorkspaceFactory.create().id)}

    response = client.post("/api/v1/datasets", json=dataset_json)

    assert response.status_code == 401
    assert db.query(Dataset).count() == 0


def test_create_dataset_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    dataset_json = {"name": "name", "workspace_id": str(WorkspaceFactory.create().id)}

    response = client.post("/api/v1/datasets", headers={API_KEY_HEADER_NAME: annotator.api_key}, json=dataset_json)

    assert response.status_code == 403
    assert db.query(Dataset).count() == 0


def test_create_dataset_with_existent_name(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create(name="name")
    dataset_json = {"name": "name", "workspace_id": str(dataset.workspace_id)}

    response = client.post("/api/v1/datasets", headers=admin_auth_header, json=dataset_json)

    assert response.status_code == 409
    assert db.query(Dataset).count() == 1


def test_create_dataset_with_nonexistent_workspace_id(client: TestClient, db: Session, admin_auth_header: dict):
    dataset_json = {"name": "name", "workspace_id": str(uuid4())}

    response = client.post("/api/v1/datasets", headers=admin_auth_header, json=dataset_json)

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
    admin_auth_header: dict,
    settings: dict,
    expected_settings: dict,
):
    dataset = DatasetFactory.create()
    field_json = {"name": "name", "title": "title", "settings": settings}

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=admin_auth_header, json=field_json)

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
def test_create_dataset_field_with_invalid_name(
    client: TestClient, db: Session, admin_auth_header: dict, invalid_name: str
):
    dataset = DatasetFactory.create()
    field_json = {
        "name": invalid_name,
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=admin_auth_header, json=field_json)

    assert response.status_code == 422
    assert db.query(Field).count() == 0


def test_create_dataset_field_with_invalid_max_length_name(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    field_json = {
        "name": "a" * (FIELD_CREATE_NAME_MAX_LENGTH + 1),
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=admin_auth_header, json=field_json)

    assert response.status_code == 422
    assert db.query(Field).count() == 0


def test_create_dataset_field_with_invalid_max_length_title(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    field_json = {
        "name": "name",
        "title": "a" * (FIELD_CREATE_TITLE_MAX_LENGTH + 1),
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=admin_auth_header, json=field_json)

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
def test_create_dataset_field_with_invalid_settings(
    client: TestClient, db: Session, admin_auth_header: dict, settings: dict
):
    dataset = DatasetFactory.create()
    field_json = {
        "name": "name",
        "title": "Title",
        "settings": settings,
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=admin_auth_header, json=field_json)

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
def test_create_dataset_field_with_invalid_settings(
    client: TestClient, db: Session, admin_auth_header: dict, settings: dict
):
    dataset = DatasetFactory.create()
    field_json = {
        "name": "name",
        "title": "Title",
        "settings": settings,
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=admin_auth_header, json=field_json)

    assert response.status_code == 422
    assert db.query(Field).count() == 0


def test_create_dataset_field_with_existent_name(client: TestClient, db: Session, admin_auth_header: dict):
    field = FieldFactory.create(name="name")
    field_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{field.dataset.id}/fields", headers=admin_auth_header, json=field_json)

    assert response.status_code == 409
    assert db.query(Field).count() == 1


def test_create_dataset_field_with_published_dataset(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    field_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/fields", headers=admin_auth_header, json=field_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Field cannot be created for a published dataset"}
    assert db.query(Field).count() == 0


def test_create_dataset_field_with_nonexistent_dataset_id(client: TestClient, db: Session, admin_auth_header: dict):
    DatasetFactory.create()
    field_json = {
        "name": "text",
        "title": "Text",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{uuid4()}/fields", headers=admin_auth_header, json=field_json)

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
                    {
                        "value": "positive",
                        "text": "Positive",
                    },
                    {
                        "value": "negative",
                        "text": "Negative",
                    },
                    {
                        "value": "neutral",
                        "text": "Neutral",
                    },
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
    ],
)
def test_create_dataset_question(
    client: TestClient,
    db: Session,
    admin_auth_header: dict,
    settings: dict,
    expected_settings: dict,
):
    dataset = DatasetFactory.create()
    question_json = {
        "name": "name",
        "title": "title",
        "settings": settings,
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=admin_auth_header, json=question_json)

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


def test_create_dataset_question_with_description(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    question_json = {
        "name": "name",
        "title": "title",
        "description": "description",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=admin_auth_header, json=question_json)

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
    client: TestClient, db: Session, admin_auth_header: dict, invalid_name: str
):
    dataset = DatasetFactory.create()
    question_json = {
        "name": invalid_name,
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=admin_auth_header, json=question_json)

    assert response.status_code == 422
    assert db.query(Question).count() == 0


def test_create_dataset_question_with_invalid_max_length_name(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    question_json = {
        "name": "a" * (QUESTION_CREATE_NAME_MAX_LENGTH + 1),
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=admin_auth_header, json=question_json)

    assert response.status_code == 422
    assert db.query(Question).count() == 0


def test_create_dataset_question_with_invalid_max_length_title(
    client: TestClient, db: Session, admin_auth_header: dict
):
    dataset = DatasetFactory.create()
    question_json = {
        "name": "name",
        "title": "a" * (QUESTION_CREATE_TITLE_MAX_LENGTH + 1),
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=admin_auth_header, json=question_json)

    assert response.status_code == 422
    assert db.query(Question).count() == 0


def test_create_dataset_question_with_invalid_max_length_description(
    client: TestClient, db: Session, admin_auth_header: dict
):
    dataset = DatasetFactory.create()
    question_json = {
        "name": "name",
        "title": "title",
        "description": "a" * (QUESTION_CREATE_DESCRIPTION_MAX_LENGTH + 1),
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=admin_auth_header, json=question_json)

    assert response.status_code == 422
    assert db.query(Question).count() == 0


def test_create_dataset_question_with_existent_name(client: TestClient, db: Session, admin_auth_header: dict):
    question = QuestionFactory.create(name="name")
    question_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(
        f"/api/v1/datasets/{question.dataset.id}/questions", headers=admin_auth_header, json=question_json
    )

    assert response.status_code == 409
    assert db.query(Question).count() == 1


def test_create_dataset_question_with_published_dataset(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    question_json = {
        "name": "name",
        "title": "title",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=admin_auth_header, json=question_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Question cannot be created for a published dataset"}
    assert db.query(Question).count() == 0


def test_create_dataset_question_with_nonexistent_dataset_id(client: TestClient, db: Session, admin_auth_header: dict):
    DatasetFactory.create()
    question_json = {
        "name": "text",
        "title": "Text",
        "settings": {"type": "text"},
    }

    response = client.post(f"/api/v1/datasets/{uuid4()}/questions", headers=admin_auth_header, json=question_json)

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
                {"value": "".join(["a" for _ in range(LABEL_SELECTION_VALUE_MAX_LENGHT + 1)]), "text": "a"},
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
                {"value": "a", "text": "".join(["a" for _ in range(LABEL_SELECTION_TEXT_MAX_LENGTH + 1)])},
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
                    "description": "".join(["a" for _ in range(LABEL_SELECTION_DESCRIPTION_MAX_LENGTH + 1)]),
                },
                {"value": "b", "text": "b"},
            ],
        },
    ],
)
def test_create_dataset_question_with_invalid_settings(
    client: TestClient,
    db: Session,
    admin_auth_header: dict,
    settings: dict,
):
    dataset = DatasetFactory.create()
    question_json = {"name": "question", "title": "Question", "settings": settings}

    response = client.post(f"/api/v1/datasets/{dataset.id}/questions", headers=admin_auth_header, json=question_json)

    assert response.status_code == 422
    assert db.query(Question).count() == 0


@pytest.mark.asyncio
async def test_create_dataset_records(
    client: TestClient,
    search_engine: SearchEngine,
    opensearch: OpenSearch,
    # TODO: use the overwrite deps to provide a spied local telemetry client.
    test_telemetry: MagicMock,
    db: Session,
    admin: User,
    admin_auth_header: dict,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)

    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)
    # Prepare dataset and es index
    await search_engine.create_index(dataset)

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

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 204, response.json()
    assert db.query(Record).count() == 5
    assert db.query(Response).count() == 4

    index_name = f"rg.{dataset.id}"
    opensearch.indices.refresh(index=index_name)
    es_docs = [hit["_source"] for hit in opensearch.search(index=index_name)["hits"]["hits"]]
    assert es_docs == [
        {
            "id": str(db.get(Record, UUID(es_docs[0]["id"])).id),
            "fields": {"input": "Say Hello", "output": "Hello"},
            "responses": {"admin": {"values": {"input_ok": "yes", "output_ok": "yes"}, "status": "submitted"}},
        },
        {
            "id": str(db.get(Record, UUID(es_docs[1]["id"])).id),
            "fields": {"input": "Say Hello", "output": "Hi"},
            "responses": {},
        },
        {
            "id": str(db.get(Record, UUID(es_docs[2]["id"])).id),
            "fields": {"input": "Say Pello", "output": "Hello World"},
            "responses": {"admin": {"values": {"input_ok": "no", "output_ok": "no"}, "status": "submitted"}},
        },
        {
            "id": str(db.get(Record, UUID(es_docs[3]["id"])).id),
            "fields": {"input": "Say Hello", "output": "Good Morning"},
            "responses": {"admin": {"values": {"input_ok": "yes", "output_ok": "no"}, "status": "discarded"}},
        },
        {
            "id": str(db.get(Record, UUID(es_docs[4]["id"])).id),
            "fields": {"input": "Say Hello", "output": "Say Hello"},
            "responses": {"admin": {"values": None, "status": "discarded"}},
        },
    ]

    test_telemetry.assert_called_once_with(action="DatasetRecordsCreated", data={"records": len(records_json["items"])})


@pytest.mark.asyncio
async def test_create_dataset_records_with_response_for_multiple_users(
    client: TestClient,
    search_engine: SearchEngine,
    opensearch: OpenSearch,
    db: Session,
    admin: User,
    admin_auth_header: dict,
):
    workspace = WorkspaceFactory.create()

    dataset = DatasetFactory.create(status=DatasetStatus.ready, workspace=workspace)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    annotator = AnnotatorFactory.create(workspaces=[workspace])

    # Prepare dataset and es index
    await search_engine.create_index(dataset)

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

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 204, response.json()
    assert db.query(Record).count() == 2
    assert db.query(Response).filter(Response.user_id == annotator.id).count() == 2
    assert db.query(Response).filter(Response.user_id == admin.id).count() == 1


@pytest.mark.asyncio
async def test_create_dataset_records_with_response_for_unknown_user(
    client: TestClient,
    search_engine: SearchEngine,
    opensearch: OpenSearch,
    db: Session,
    admin_auth_header: dict,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    # Prepare dataset and es index
    await search_engine.create_index(dataset)

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

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 422, response.json()
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


@pytest.mark.asyncio
async def test_create_dataset_records_with_duplicated_response_for_an_user(
    client: TestClient,
    search_engine: SearchEngine,
    opensearch: OpenSearch,
    db: Session,
    admin: User,
    admin_auth_header: dict,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)
    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    # Prepare dataset and es index
    await search_engine.create_index(dataset)

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
                    },
                    {
                        "values": {"input_ok": {"value": "no"}, "output_ok": {"value": "no"}},
                        "status": "submitted",
                        "user_id": str(admin.id),
                    },
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 422, response.json()
    assert response.json() == {
        "detail": {
            "code": "argilla.api.errors::ValidationError",
            "params": {
                "model": "Request",
                "errors": [
                    {
                        "loc": ["body", "items", 0, "responses"],
                        "msg": f"Responses contains several responses for the same user_id: {str(admin.id)!r}",
                        "type": "value_error",
                    }
                ],
            },
        }
    }
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_missing_required_fields(
    client: TestClient, db: Session, opensearch: OpenSearch, admin_auth_header: dict
):
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

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Missing required value for field: 'output'"}
    assert db.query(Record).count() == 0


def test_create_dataset_records_with_wrong_value_field(
    client: TestClient, db: Session, opensearch: OpenSearch, admin_auth_header: dict
):
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

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Wrong value found for field 'output'. Expected 'str', found 'int'"}
    assert db.query(Record).count() == 0


def test_create_dataset_records_with_extra_fields(
    client: TestClient, db: Session, opensearch: OpenSearch, admin_auth_header: dict
):
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

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Error: found fields values for non configured fields: ['output']"}
    assert db.query(Record).count() == 0


@pytest.mark.asyncio
async def test_create_dataset_records_with_index_error(
    client: TestClient,
    opensearch: OpenSearch,
    db: Session,
    admin_auth_header: dict,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)

    records_json = {
        "items": [
            {"fields": {"input": "Say Hello", "output": "Hello"}},
            {"fields": {"input": "Say Hello", "output": "Hi"}},
            {"fields": {"input": "Say Pello", "output": "Hello World"}},
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 422
    assert db.query(Record).count() == 0

    index_name = f"rg.{dataset.id}"

    assert not opensearch.indices.exists(index=index_name)


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


@pytest.mark.asyncio
async def test_create_dataset_records_with_submitted_response(
    client: TestClient,
    db: Session,
    search_engine: SearchEngine,
    opensearch: OpenSearch,
    admin: User,
    admin_auth_header: dict,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)

    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    # Prepare dataset and es index
    await search_engine.create_index(dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": "Hello"},
                "responses": [
                    {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                        "status": "submitted",
                        "user_id": str(admin.id),
                    }
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 204
    assert db.query(Record).count() == 1
    assert db.query(Response).count() == 1


def test_create_dataset_records_with_submitted_response_without_values(
    client: TestClient,
    db: Session,
    admin: User,
    admin_auth_header: dict,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "ouput": "Hello"},
                "responses": [
                    {
                        "user_id": str(admin.id),
                        "status": "submitted",
                    }
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 422
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


@pytest.mark.asyncio
async def test_create_dataset_records_with_discarded_response(
    client: TestClient,
    db: Session,
    search_engine: SearchEngine,
    opensearch: OpenSearch,
    admin: User,
    admin_auth_header: dict,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)

    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    await search_engine.create_index(dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": "Hello"},
                "responses": [
                    {
                        "values": {"input_ok": {"value": "yes"}, "output_ok": {"value": "yes"}},
                        "status": "discarded",
                        "user_id": str(admin.id),
                    }
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 204
    assert db.query(Record).count() == 1
    assert db.query(Response).filter(Response.status == ResponseStatus.discarded).count() == 1


def test_create_dataset_records_with_invalid_response_status(
    client: TestClient,
    db: Session,
    admin: User,
    admin_auth_header: dict,
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
                        "user_id": str(admin.id),
                    }
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 422
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


@pytest.mark.asyncio
async def test_create_dataset_records_with_discarded_response_without_values(
    client: TestClient,
    db: Session,
    search_engine: SearchEngine,
    opensearch: OpenSearch,
    admin: User,
    admin_auth_header: dict,
):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    TextFieldFactory.create(name="input", dataset=dataset)
    TextFieldFactory.create(name="output", dataset=dataset)

    TextQuestionFactory.create(name="input_ok", dataset=dataset)
    TextQuestionFactory.create(name="output_ok", dataset=dataset)

    await search_engine.create_index(dataset)

    records_json = {
        "items": [
            {
                "fields": {"input": "Say Hello", "output": "Hello"},
                "responses": [
                    {
                        "status": "discarded",
                        "user_id": str(admin.id),
                    }
                ],
            },
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 204
    assert db.query(Record).count() == 1
    assert db.query(Response).count() == 1


def test_create_dataset_records_with_non_published_dataset(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create(status=DatasetStatus.draft)
    records_json = {
        "items": [
            {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": "1"},
        ],
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 422
    assert response.json() == {"detail": "Records cannot be created for a non published dataset"}
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_less_items_than_allowed(client: TestClient, db: Session, admin_auth_header: dict):
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

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 422
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_more_items_than_allowed(client: TestClient, db: Session, admin_auth_header: dict):
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

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 422
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_invalid_records(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    records_json = {
        "items": [
            {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": 1},
            {"fields": "invalid", "external_id": 2},
            {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": 3},
        ]
    }

    response = client.post(f"/api/v1/datasets/{dataset.id}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 422
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_create_dataset_records_with_nonexistent_dataset_id(client: TestClient, db: Session, admin_auth_header: dict):
    DatasetFactory.create()
    records_json = {
        "items": [
            {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": 1},
            {"fields": {"input": "Say Hello", "ouput": "Hello"}, "external_id": 2},
        ]
    }

    response = client.post(f"/api/v1/datasets/{uuid4()}/records", headers=admin_auth_header, json=records_json)

    assert response.status_code == 404
    assert db.query(Record).count() == 0
    assert db.query(Response).count() == 0


def test_publish_dataset(
    client: TestClient,
    db: Session,
    opensearch: OpenSearch,
    # TODO: use the overwrite deps to provide a spied local telemetry client.
    test_telemetry: MagicMock,
    admin_auth_header: dict,
):
    dataset = DatasetFactory.create()
    TextFieldFactory.create(dataset=dataset)
    RatingQuestionFactory.create(dataset=dataset)

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=admin_auth_header)

    assert response.status_code == 200
    assert db.get(Dataset, dataset.id).status == "ready"

    response_body = response.json()
    assert response_body["status"] == "ready"

    assert opensearch.indices.exists(index=f"rg.{dataset.id}")
    test_telemetry.assert_called_once_with(action="PublishedDataset", data={"questions": ["rating"]})


def test_publish_dataset_with_error_on_index_creation(
    client: TestClient,
    db: Session,
    opensearch: OpenSearch,
    admin_auth_header: dict,
):
    dataset = DatasetFactory.create()
    TextFieldFactory.create(dataset=dataset)
    QuestionFactory.create(settings={"type": "invalid"}, dataset=dataset)

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=admin_auth_header)

    assert response.status_code == 422
    assert db.get(Dataset, dataset.id).status == "draft"

    assert not opensearch.indices.exists(index=f"rg.{dataset.id}")


def test_publish_dataset_without_authentication(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    QuestionFactory.create(dataset=dataset)

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish")

    assert response.status_code == 401
    assert db.get(Dataset, dataset.id).status == "draft"


def test_publish_dataset_as_annotator(client: TestClient, db: Session):
    dataset = DatasetFactory.create()
    QuestionFactory.create(dataset=dataset)
    annotator = AnnotatorFactory.create(workspaces=[dataset.workspace])

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403
    assert db.get(Dataset, dataset.id).status == "draft"


def test_publish_dataset_already_published(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create(status=DatasetStatus.ready)
    QuestionFactory.create(dataset=dataset)

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=admin_auth_header)

    assert response.status_code == 422
    assert response.json() == {"detail": "Dataset is already published"}
    assert db.get(Dataset, dataset.id).status == "ready"


def test_publish_dataset_without_fields(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    RatingQuestionFactory.create(dataset=dataset)

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=admin_auth_header)

    assert response.status_code == 422
    assert response.json() == {"detail": "Dataset cannot be published without fields"}
    assert db.get(Dataset, dataset.id).status == "draft"


def test_publish_dataset_without_questions(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    TextFieldFactory.create(dataset=dataset)

    response = client.put(f"/api/v1/datasets/{dataset.id}/publish", headers=admin_auth_header)

    assert response.status_code == 422
    assert response.json() == {"detail": "Dataset cannot be published without questions"}
    assert db.get(Dataset, dataset.id).status == "draft"


def test_publish_dataset_with_nonexistent_dataset_id(client: TestClient, db: Session, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    QuestionFactory.create(dataset=dataset)

    response = client.put(f"/api/v1/datasets/{uuid4()}/publish", headers=admin_auth_header)

    assert response.status_code == 404
    assert db.get(Dataset, dataset.id).status == "draft"


def test_delete_dataset(client: TestClient, db: Session, opensearch: OpenSearch, admin: User, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    TextFieldFactory.create(dataset=dataset)
    TextQuestionFactory.create(dataset=dataset)

    other_dataset = DatasetFactory.create()
    other_field = TextFieldFactory.create(dataset=other_dataset)
    other_question = TextQuestionFactory.create(dataset=other_dataset)
    other_record = RecordFactory.create(dataset=other_dataset)
    other_response = ResponseFactory.create(record=other_record, user=admin)

    response = client.delete(f"/api/v1/datasets/{dataset.id}", headers=admin_auth_header)

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
    assert not opensearch.indices.exists(index=f"rg.{dataset.id}")


def test_delete_published_dataset(client: TestClient, db: Session, admin: User, admin_auth_header: dict):
    dataset = DatasetFactory.create()
    TextFieldFactory.create(dataset=dataset)
    TextQuestionFactory.create(dataset=dataset)
    record = RecordFactory.create(dataset=dataset)
    ResponseFactory.create(record=record, user=admin)

    other_dataset = DatasetFactory.create()
    other_field = TextFieldFactory.create(dataset=other_dataset)
    other_question = TextQuestionFactory.create(dataset=other_dataset)
    other_record = RecordFactory.create(dataset=other_dataset)
    other_response = ResponseFactory.create(record=other_record, user=admin)

    response = client.delete(f"/api/v1/datasets/{dataset.id}", headers=admin_auth_header)

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


def test_delete_dataset_without_authentication(client: TestClient, db: Session):
    dataset = DatasetFactory.create()

    response = client.delete(f"/api/v1/datasets/{dataset.id}")

    assert response.status_code == 401
    assert db.query(Dataset).count() == 1


def test_delete_dataset_as_annotator(client: TestClient, db: Session):
    annotator = AnnotatorFactory.create()
    dataset = DatasetFactory.create()

    response = client.delete(f"/api/v1/datasets/{dataset.id}", headers={API_KEY_HEADER_NAME: annotator.api_key})

    assert response.status_code == 403
    assert db.query(Dataset).count() == 1


def test_delete_dataset_with_nonexistent_dataset_id(client: TestClient, db: Session, admin_auth_header: dict):
    DatasetFactory.create()

    response = client.delete(f"/api/v1/datasets/{uuid4()}", headers=admin_auth_header)

    assert response.status_code == 404
    assert db.query(Dataset).count() == 1
