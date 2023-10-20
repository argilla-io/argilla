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
from argilla import (
    FeedbackDataset,
    FeedbackRecord,
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
    TextField,
    TextQuestion,
    Workspace,
)
from argilla.client import api
from argilla.client.client import Argilla
from argilla.client.sdk.v1.records.api import delete_record, delete_suggestions
from argilla.client.sdk.v1.records.models import FeedbackItemModel
from argilla.server.models import User, UserRole

from tests.factories import (
    DatasetFactory,
    RatingQuestionFactory,
    RecordFactory,
    SuggestionFactory,
    UserFactory,
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


@pytest.mark.asyncio
class TestRecordsSDK:
    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete_record(self, owner: User, test_dataset: FeedbackDataset, role: UserRole) -> None:
        user = await UserFactory.create(role=role)

        api.init(api_key=owner.api_key)

        workspace = Workspace.create("test-workspace")
        workspace.add_user(user.id)

        api.init(api_key=user.api_key, workspace=workspace.name)
        remote = test_dataset.push_to_argilla(name="test-dataset", workspace=workspace)
        remote.add_records(
            [
                FeedbackRecord(fields={"text": "Hello world!"}),
                FeedbackRecord(fields={"text": "Hello world!"}),
            ]
        )
        argilla_api = api.active_api()

        for record in remote.records:
            response = delete_record(client=argilla_api.client.httpx, id=record.id)
            assert response.status_code == 200
            assert isinstance(response.parsed, FeedbackItemModel)
            assert response.parsed.id == record.id

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete_suggestions(self, role: UserRole) -> None:
        dataset = await DatasetFactory.create()
        records = await RecordFactory.create_batch(dataset=dataset, size=10)
        suggestions = []
        for record in records:
            suggestions.append(await SuggestionFactory.create(record=record))
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)

        for suggestion in suggestions:
            response = delete_suggestions(
                client=api.client.httpx, id=suggestion.record.id, suggestion_ids=[suggestion.id]
            )
            assert response.status_code == 204

    @pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
    async def test_delete_suggestions_batch(self, role: UserRole) -> None:
        dataset = await DatasetFactory.create()
        questions = await RatingQuestionFactory.create_batch(size=3, dataset=dataset, required=True)
        record = await RecordFactory.create(dataset=dataset)
        suggestions = []
        for question, value in zip(questions, [1, 2, 3]):
            suggestions.append(await SuggestionFactory.create(record=record, question=question, value=value))
        user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

        api = Argilla(api_key=user.api_key, workspace=dataset.workspace.name)

        response = delete_suggestions(
            client=api.client.httpx, id=record.id, suggestion_ids=[suggestion.id for suggestion in suggestions]
        )
        assert response.status_code == 204
