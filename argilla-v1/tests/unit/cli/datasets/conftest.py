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
from typing import TYPE_CHECKING
from uuid import uuid4

import httpx
import pytest
from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla_v1.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla_v1.client.feedback.schemas.remote.fields import RemoteTextField
from argilla_v1.client.feedback.schemas.remote.questions import RemoteTextQuestion
from argilla_v1.client.sdk.datasets.models import Dataset

if TYPE_CHECKING:
    from argilla_v1.client.workspaces import Workspace


@pytest.fixture
def remote_feedback_dataset(workspace: "Workspace") -> RemoteFeedbackDataset:
    return RemoteFeedbackDataset(
        client=httpx.Client(),
        id=uuid4(),
        name="unit-test",
        workspace=workspace,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        fields=[RemoteTextField(id=uuid4(), name="prompt")],
        questions=[RemoteTextQuestion(id=uuid4(), name="corrected")],
    )


@pytest.fixture
def feedback_dataset(remote_feedback_dataset: RemoteFeedbackDataset) -> FeedbackDataset:
    return FeedbackDataset(
        fields=[field.to_local() for field in remote_feedback_dataset.fields],
        questions=[question.to_local() for question in remote_feedback_dataset.questions],
    )


@pytest.fixture
def dataset() -> Dataset:
    return Dataset(
        name="unit-test",
        id="rg.unit-test",
        task="TextClassification",
        owner="unit-test",
        workspace="unit-test",
        created_at=datetime.now(),
        last_updated=datetime.now(),
    )
