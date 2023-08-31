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
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.feedback.schemas.fields import TextField
from argilla.client.feedback.schemas.questions import TextQuestion
from argilla.client.sdk.datasets.models import Dataset
from argilla.client.workspaces import Workspace


@pytest.fixture
def remote_feedback_dataset() -> "RemoteFeedbackDataset":
    workspace = Workspace.__new__(Workspace)
    workspace.__dict__.update(
        {
            "id": uuid4(),
            "name": "unit-test",
            "inserted_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    )
    return RemoteFeedbackDataset(
        client=httpx.Client(),
        id=uuid4(),
        name="unit-test",
        workspace=workspace,
        fields=[TextField(name="prompt")],
        questions=[TextQuestion(name="corrected")],
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
