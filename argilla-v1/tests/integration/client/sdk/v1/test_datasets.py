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

import argilla_v1.client.singleton
import pytest
from argilla_server.models import DatasetStatus, User, UserRole
from argilla_v1 import (
    FeedbackDataset,
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
    TextField,
    TextQuestion,
    Workspace,
)
from argilla_v1.client.client import Argilla
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.sdk.v1.datasets.api import (
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
    update_records,
)
from argilla_v1.client.sdk.v1.datasets.models import (
    FeedbackDatasetModel,
    FeedbackFieldModel,
    FeedbackItemModel,
    FeedbackMetadataPropertyModel,
    FeedbackMetricsModel,
    FeedbackQuestionModel,
    FeedbackRecordsModel,
    FeedbackSuggestionModel,
)
from argilla_v1.client.sdk.v1.records.api import set_suggestion

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


@pytest.fixture()
def test_dataset():
    dataset = FeedbackDataset(
        fields=[TextField(name="text"), TextField(name="optional", required=False)],
        questions=[TextQuestion(name="question")],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="integer-metadata"),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )
    return dataset


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
    response = create_dataset(
        client=api.client.httpx,
        name="dataset_name",
        workspace_id=str(workspace.id),
        guidelines="integration-test",
        allow_extra_metadata=True,
    )

    assert response.status_code == 201
    assert isinstance(response.parsed, FeedbackDatasetModel)
    assert response.parsed.name == "dataset_name"
    assert response.parsed.status == DatasetStatus.draft
    assert response.parsed.guidelines == "integration-test"
    assert response.parsed.allow_extra_metadata is True


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
            "title": "test_metadata_property_title",
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
async def test_add_records(owner: User, test_dataset: FeedbackDataset, role: UserRole) -> None:
    user = await UserFactory.create(role=role)

    argilla_v1.client.singleton.init(api_key=owner.api_key)
    workspace = Workspace.create(name="test-workspace")
    workspace.add_user(user.id)

    argilla_v1.client.singleton.init(api_key=user.api_key)
    remote = test_dataset.push_to_argilla(name="test-dataset", workspace=workspace)
    argilla_api = argilla_v1.client.singleton.active_api()

    response = add_records(client=argilla_api.client.httpx, id=remote.id, records=[{"fields": {"text": "test_value"}}])

    assert response.status_code == 204


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_update_records(test_dataset: FeedbackDataset, role: UserRole) -> None:
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create(role=role, workspaces=[workspace])

    test_dataset.add_records(
        [
            {
                "fields": {"text": "test_value_1", "optional": "optional_1"},
                "metadata": {"terms-metadata": "a", "integer-metadata": 0, "float-metadata": 0.0},
                "suggestions": [{"question_name": "question", "value": "suggestion 1"}],
            },
            {
                "fields": {"text": "test_value_2", "optional": "optional_2"},
                "metadata": {"terms-metadata": "b", "integer-metadata": 1, "float-metadata": 1.0},
                "suggestions": [{"question_name": "question", "value": "suggestion 1"}],
            },
            {
                "fields": {"text": "test_value_3", "optional": "optional_3"},
                "metadata": {"terms-metadata": "c", "integer-metadata": 2, "float-metadata": 2.0},
                "suggestions": [{"question_name": "question", "value": "suggestion 1"}],
            },
        ]
    )

    argilla_v1.client.singleton.init(api_key=user.api_key)
    remote = test_dataset.push_to_argilla(name="test-dataset", workspace=workspace.name)

    records_to_update = []
    for record in remote.records:
        records_to_update.append(
            {
                "id": str(record.id),
                "metadata": {"terms-metadata": "c", "integer-metadata": 9, "float-metadata": 9.0},
                "suggestions": [{"question_id": str(remote.questions[0].id), "value": "new suggestion"}],
            }
        )

    argilla_api = argilla_v1.client.singleton.active_api()
    response = update_records(client=argilla_api.client.httpx, id=remote.id, records=records_to_update)

    assert response.status_code == 204


@pytest.mark.skip(reason="Enable when factories are removed from the test")
@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_get_records(role: UserRole) -> None:
    # TODO: Remote this test. It does not make sense as integration test
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


# TODO: check if we can include a callback to the factory to index the metadata in Elastic Search
# TODO: check why the metadata filters are not working, most likely because the metadata is not indexed


@pytest.mark.parametrize("role", [UserRole.admin, UserRole.owner])
@pytest.mark.asyncio
async def test_add_suggestion(role: UserRole) -> None:
    workspace = await WorkspaceFactory.create()
    user = await UserFactory.create(role=role, workspaces=[workspace])

    argilla_v1.client.singleton.init(api_key=user.api_key, workspace=workspace.name)

    dataset = FeedbackDataset(fields=[TextField(name="text-field")], questions=[TextQuestion(name="text-question")])

    dataset.add_records(
        [
            FeedbackRecord(
                fields={"text-field": "unit-test"},
            )
            for _ in range(10)
        ]
    )

    remote = dataset.push_to_argilla(name="test-dataset", workspace=workspace.name)

    api = Argilla(api_key=user.api_key, workspace=workspace.name)

    for record in remote.records:
        response = set_suggestion(
            client=api.http_client.httpx, record_id=record.id, question_id=remote.questions[0].id, value="unit-test"
        )
        assert response.status_code == 201
        assert isinstance(response.parsed, FeedbackSuggestionModel)
        assert response.parsed.value == "unit-test"
        assert response.parsed.question_id == str(remote.questions[0].id)


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
