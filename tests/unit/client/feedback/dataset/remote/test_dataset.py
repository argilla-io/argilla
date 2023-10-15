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
from uuid import uuid4

import httpx
import pytest
from argilla import Workspace
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.feedback.schemas import SuggestionSchema
from argilla.client.feedback.schemas.remote.fields import RemoteTextField
from argilla.client.feedback.schemas.remote.questions import RemoteTextQuestion
from argilla.client.feedback.schemas.remote.records import RemoteFeedbackRecord
from argilla.client.sdk.users.models import UserModel, UserRole
from argilla.client.sdk.v1.datasets.models import FeedbackItemModel, FeedbackSuggestionModel
from argilla.client.sdk.v1.workspaces.models import WorkspaceModel


@pytest.fixture()
def test_remote_dataset(mock_httpx_client: httpx.Client) -> RemoteFeedbackDataset:
    return RemoteFeedbackDataset(
        client=mock_httpx_client,
        id=uuid4(),
        name="test-remote-dataset",
        workspace=Workspace._new_instance(
            client=mock_httpx_client,
            ws=WorkspaceModel(
                id=uuid4(),
                name="test-remote-workspace",
                inserted_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ),
        fields=[RemoteTextField(id=uuid4(), name="text")],
        questions=[RemoteTextQuestion(id=uuid4(), name="text")],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture()
def test_remote_record(
    mock_httpx_client: httpx.Client, test_remote_dataset: RemoteFeedbackDataset
) -> RemoteFeedbackRecord:
    return RemoteFeedbackRecord(
        id=uuid4(),
        client=mock_httpx_client,
        fields={"text": "test"},
        metadata={"new": "metadata"},
        question_name_to_id=test_remote_dataset._question_name_to_id,
    )


class TestSuiteRemoteDataset:
    def test_update_records(
        self,
        mock_httpx_client: httpx.Client,
        test_remote_dataset: RemoteFeedbackDataset,
        test_remote_record: RemoteFeedbackRecord,
    ) -> None:
        """Test updating records."""

        mock_httpx_client.get.return_value = httpx.Response(
            status_code=200,
            content=UserModel(
                id=uuid4(),
                first_name="test",
                username="test",
                role=UserRole.owner,
                api_key="api.key",
                inserted_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ).json(),
        )

        mock_httpx_client.patch.return_value = httpx.Response(
            status_code=200,
            content=FeedbackItemModel(
                id=test_remote_record.id,
                fields=test_remote_record.fields,
                inserted_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ).json(),
        )

        test_remote_dataset.update_records(records=[test_remote_record])

        mock_httpx_client.patch.assert_called_once_with(
            url=f"/api/v1/records/{test_remote_record.id}",
            json={"metadata": {"new": "metadata"}},
        )

    def test_update_multiple_records(
        self,
        mock_httpx_client: httpx.Client,
        test_remote_dataset: RemoteFeedbackDataset,
        test_remote_record: RemoteFeedbackRecord,
    ) -> None:
        """Test updating records."""

        mock_httpx_client.get.return_value = httpx.Response(
            status_code=200,
            content=UserModel(
                id=uuid4(),
                first_name="test",
                username="test",
                role=UserRole.owner,
                api_key="api.key",
                inserted_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ).json(),
        )

        mock_httpx_client.patch.return_value = httpx.Response(
            status_code=200,
            content=FeedbackItemModel(
                id=test_remote_record.id,
                fields=test_remote_record.fields,
                inserted_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ).json(),
        )

        test_remote_dataset.update_records(records=[test_remote_record] * 10)

        assert mock_httpx_client.patch.call_count == 10

    def test_update_records_with_multiple_suggestions(
        self,
        mock_httpx_client: httpx.Client,
        test_remote_dataset: RemoteFeedbackDataset,
        test_remote_record: RemoteFeedbackRecord,
    ) -> None:
        """Test updating records."""

        mock_httpx_client.get.return_value = httpx.Response(
            status_code=200,
            content=UserModel(
                id=uuid4(),
                first_name="test",
                username="test",
                role=UserRole.owner,
                api_key="api.key",
                inserted_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ).json(),
        )

        mock_httpx_client.patch.return_value = httpx.Response(
            status_code=200,
            content=FeedbackItemModel(
                id=test_remote_record.id,
                fields=test_remote_record.fields,
                inserted_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ).json(),
        )

        expected_suggestion = FeedbackSuggestionModel(
            id=uuid4(),
            question_id=test_remote_dataset.question_by_name("text").id,
            value="Test value",
            score=0.5,
            agent="test",
        )
        mock_httpx_client.put.return_value = httpx.Response(status_code=200, content=expected_suggestion.json())

        test_remote_record.suggestions = [
            SuggestionSchema(question_name="text", value="Test value", score=0.5, agent="test")
        ] * 10

        test_remote_dataset.update_records(records=[test_remote_record] * 10)

        # TODO: Reduce the number of call -> bulk endpoint at least for suggestions
        assert mock_httpx_client.put.call_count == 100

    def test_update_records_suggestions(
        self,
        mock_httpx_client: httpx.Client,
        test_remote_dataset: RemoteFeedbackDataset,
        test_remote_record: RemoteFeedbackRecord,
    ) -> None:
        mock_httpx_client.get.return_value = httpx.Response(
            status_code=200,
            content=UserModel(
                id=uuid4(),
                first_name="test",
                username="test",
                role=UserRole.owner,
                api_key="api.key",
                inserted_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ).json(),
        )

        expected_suggestion = FeedbackSuggestionModel(
            id=uuid4(),
            question_id=test_remote_dataset.question_by_name("text").id,
            value="Test value",
            score=0.5,
            agent="test",
        )
        mock_httpx_client.patch.return_value = httpx.Response(
            status_code=200,
            content=FeedbackItemModel(
                id=test_remote_record.id,
                fields=test_remote_record.fields,
                inserted_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ).json(),
        )
        mock_httpx_client.put.return_value = httpx.Response(status_code=200, content=expected_suggestion.json())

        test_remote_record.suggestions = [
            SuggestionSchema(question_name="text", value="Test value", score=0.5, agent="test")
        ]

        test_remote_dataset.update_records(records=test_remote_record)

        mock_httpx_client.patch.assert_called
        mock_httpx_client.put.assert_called_with(
            url=f"/api/v1/records/{test_remote_record.id}/suggestions",
            # TODO: This should be a list of suggestions
            json={
                "agent": expected_suggestion.agent,
                "question_id": str(expected_suggestion.question_id),
                "score": expected_suggestion.score,
                "value": expected_suggestion.value,
            },
        )

    def test_update_records_suggestions_with_already_suggestion(
        self,
        mock_httpx_client: httpx.Client,
        test_remote_dataset: RemoteFeedbackDataset,
        test_remote_record: RemoteFeedbackRecord,
    ) -> None:
        # TODO: Implement
        pass
