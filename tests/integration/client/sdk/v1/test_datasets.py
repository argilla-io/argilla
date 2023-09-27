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

import pytest
from argilla.client.client import Argilla
from argilla.client.sdk.v1.datasets.api import (
    add_field,
    add_metadata_property,
    add_question,
    add_records,
    create_dataset,
    delete_dataset,
    get_dataset,
    get_fields,
    get_metadata_properties,
    get_metrics,
    get_questions,
    get_records,
    list_datasets,
    publish_dataset,
    set_suggestion,
)
from argilla.client.sdk.v1.datasets.models import (
    FeedbackDatasetModel,
    FeedbackFieldModel,
    FeedbackItemModel,
    FeedbackMetadataPropertyModel,
    FeedbackMetricsModel,
    FeedbackQuestionModel,
    FeedbackRecordsModel,
    FeedbackSuggestionModel,
)
from argilla.server.models import DatasetStatus, UserRole

from tests.factories import (
    DatasetFactory,
    FloatMetadataPropertyFactory,
    IntegerMetadataPropertyFactory,
    RatingQuestionFactory,
    RecordFactory,
    TermsMetadataPropertyFactory,
    TextFieldFactory,
    UserFactory,
    WorkspaceFactory,
)


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin, UserRole.annotator])
@pytest.mark.asyncio
async def test_list_datasets(role: UserRole) -> None:
    dataset = await DatasetFactory.create()
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = list_datasets(client=api.client.httpx)

    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], FeedbackDatasetModel)


@pytest.mark.parametrize(
    "role, with_workspace, expected_length",
    [
        (UserRole.owner, False, 2),
        (UserRole.owner, True, 1),
        (UserRole.admin, False, 0),
        (UserRole.admin, True, 1),
        (UserRole.annotator, False, 0),
        (UserRole.annotator, True, 1),
    ],
)
@pytest.mark.asyncio
async def test_list_datasets_by_workspace_id(role: UserRole, with_workspace: bool, expected_length: int) -> None:
    workspace = await WorkspaceFactory.create()
    dataset = await DatasetFactory.create(workspace=workspace)
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace] if with_workspace else [])

    another_workspace = await WorkspaceFactory.create()
    await DatasetFactory.create(workspace=another_workspace)

    api = Argilla(api_key=user.api_key)
    response = list_datasets(
        client=api.client.httpx, workspace_id=str(dataset.workspace.id) if with_workspace else None
    )

    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) == expected_length
    if expected_length > 0:
        assert isinstance(response.parsed[0], FeedbackDatasetModel)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner, UserRole.annotator])
@pytest.mark.asyncio
async def test_get_datasets(role: UserRole) -> None:
    dataset = await DatasetFactory.create()
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = get_dataset(client=api.client.httpx, id=dataset.id)

    assert response.status_code == 200
    assert isinstance(response.parsed, FeedbackDatasetModel)
    assert response.parsed.name == dataset.name


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_create_dataset(role: UserRole) -> None:
    workspace = await WorkspaceFactory.create()

    user = await UserFactory.create(role=role, workspaces=[workspace])

    api = Argilla(api_key=user.api_key, workspace=workspace.name)
    response = create_dataset(client=api.client.httpx, name="dataset_name", workspace_id=str(workspace.id))

    assert response.status_code == 201
    assert isinstance(response.parsed, FeedbackDatasetModel)
    assert response.parsed.name == "dataset_name"


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_delete_dataset(role: UserRole) -> None:
    dataset = await DatasetFactory.create()
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = delete_dataset(client=api.client.httpx, id=dataset.id)

    assert response.status_code == 200

    response = api.client.httpx.get("/api/v1/me/datasets")
    assert response.status_code == 200
    assert len(response.json()["items"]) < 1


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_publish_dataset(role: UserRole) -> None:
    dataset = await DatasetFactory.create(
        status=DatasetStatus.draft,
        fields=[await TextFieldFactory.create(required=True)],
        questions=[await RatingQuestionFactory.create(required=True)],
    )
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = publish_dataset(client=api.client.httpx, id=dataset.id)

    assert response.status_code == 200
    assert isinstance(response.parsed, FeedbackDatasetModel)
    assert response.parsed.name == dataset.name
    assert response.parsed.status == "ready"


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_add_field(role: UserRole) -> None:
    dataset = await DatasetFactory.create(status=DatasetStatus.draft)
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)

    response = add_field(
        client=api.client.httpx,
        id=dataset.id,
        field={"name": "test_field", "title": "test_field", "required": True, "settings": {"type": "text"}},
    )
    assert response.status_code == 201


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner, UserRole.annotator])
@pytest.mark.asyncio
async def test_get_fields(role: UserRole) -> None:
    dataset = await DatasetFactory.create(fields=[await TextFieldFactory.create()])
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = get_fields(client=api.client.httpx, id=dataset.id)

    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], FeedbackFieldModel)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_add_question(role: UserRole) -> None:
    dataset = await DatasetFactory.create(status=DatasetStatus.draft)
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = add_question(
        client=api.client.httpx,
        id=dataset.id,
        question={
            "name": "test_question",
            "title": "test_question",
            "description": "test_description",
            "required": True,
            "settings": {"type": "text"},
        },
    )
    assert response.status_code == 201


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner, UserRole.annotator])
@pytest.mark.asyncio
async def test_get_questions(role: UserRole) -> None:
    dataset = await DatasetFactory.create(questions=[await RatingQuestionFactory.create()])
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = get_questions(client=api.client.httpx, id=dataset.id)

    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) > 0
    assert isinstance(response.parsed[0], FeedbackQuestionModel)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_add_metadata_property(role: UserRole) -> None:
    dataset = await DatasetFactory.create()
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = add_metadata_property(
        client=api.client.httpx,
        id=dataset.id,
        metadata_property={
            "name": "test_metadata_property",
            "description": "test_description",
            "settings": {"type": "terms", "values": ["a", "b", "c"]},
        },
    )
    assert response.status_code == 201


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_get_metadata_properties(role: UserRole) -> None:
    dataset = await DatasetFactory.create()
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])
    await TermsMetadataPropertyFactory.create(dataset=dataset)
    await IntegerMetadataPropertyFactory.create(dataset=dataset)
    await FloatMetadataPropertyFactory.create(dataset=dataset)

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = get_metadata_properties(client=api.client.httpx, id=dataset.id)
    assert response.status_code == 200
    assert isinstance(response.parsed, list)
    assert len(response.parsed) == 3
    assert isinstance(response.parsed[0], FeedbackMetadataPropertyModel)


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_add_records(role: UserRole) -> None:
    text_field = await TextFieldFactory.create(name="test_field")
    rating_question = await RatingQuestionFactory.create()
    dataset = await DatasetFactory.create(status=DatasetStatus.ready, fields=[text_field], questions=[rating_question])
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = add_records(client=api.client.httpx, id=dataset.id, records=[{"fields": {"test_field": "test_value"}}])

    assert response.status_code == 204


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_get_records(role: UserRole) -> None:
    dataset = await DatasetFactory.create(
        status=DatasetStatus.ready,
        fields=[await TextFieldFactory.create(required=True)],
        questions=[await RatingQuestionFactory.create(required=True)],
        records=await RecordFactory.create_batch(size=10),
    )
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = get_records(client=api.http_client.httpx, id=dataset.id)

    assert response.status_code == 200
    assert isinstance(response.parsed, FeedbackRecordsModel)
    assert len(response.parsed.items) > 0
    assert FeedbackItemModel(**response.parsed.items[0].dict())


@pytest.mark.parametrize("role", [UserRole.admin])  # , UserRole.owner])
@pytest.mark.asyncio
async def test_get_records_using_metadata_filters(role: UserRole) -> None:
    dataset = await DatasetFactory.create(status=DatasetStatus.ready)
    terms_metadata = await TermsMetadataPropertyFactory.create(dataset=dataset)
    integer_metadata = await IntegerMetadataPropertyFactory.create(dataset=dataset)
    float_metadata = await FloatMetadataPropertyFactory.create(dataset=dataset)
    await RecordFactory.create(
        dataset=dataset, metadata_={terms_metadata.name: "a", integer_metadata.name: 1, float_metadata.name: 1.0}
    )
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)
    response = get_records(
        client=api.http_client.httpx,
        id=dataset.id,
        metadata_filters=[
            f"{terms_metadata.name}:a",
            f'{integer_metadata.name}:{{"le": 0, "ge": 10}}',
            f'{float_metadata.name}:{{"le": 0.0, "ge": 10.0}}',
        ],
    )

    assert response.status_code == 200
    assert isinstance(response.parsed, FeedbackRecordsModel)
    assert len(response.parsed.items) > 0
    assert FeedbackItemModel(**response.parsed.items[0].dict())


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_add_suggestion(role: UserRole) -> None:
    dataset = await DatasetFactory.create(
        status=DatasetStatus.ready,
        fields=[await TextFieldFactory.create(required=True)],
        questions=[await RatingQuestionFactory.create(required=True)],
        records=await RecordFactory.create_batch(size=10),
    )
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)

    for record in dataset.records:
        response = set_suggestion(
            client=api.http_client.httpx, record_id=record.id, question_id=dataset.questions[0].id, value=1
        )
        assert response.status_code == 201
        assert isinstance(response.parsed, FeedbackSuggestionModel)
        assert response.parsed.value == 1
        assert response.parsed.question_id == dataset.questions[0].id


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner, UserRole.annotator])
@pytest.mark.asyncio
async def test_get_metrics(role: UserRole) -> None:
    dataset = await DatasetFactory.create(
        status=DatasetStatus.ready,
        records=await RecordFactory.create_batch(size=10),
    )
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)

    response = get_metrics(client=api.http_client.httpx, id=dataset.id)
    assert response.status_code == 200
    assert isinstance(response.parsed, FeedbackMetricsModel)
    assert response.parsed.records.count == 10
