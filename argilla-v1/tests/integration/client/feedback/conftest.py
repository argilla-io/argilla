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

from typing import TYPE_CHECKING, List

import pytest
from argilla_v1.client import singleton
from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla_v1.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.workspaces import Workspace

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes
    from argilla_v1.client.sdk.users.models import UserModel as User
    from pytest_mock import MockerFixture


@pytest.fixture
def rating_question_payload():
    return {
        "name": "label",
        "description": "label",
        "required": True,
        "values": ["1", "2"],
    }


@pytest.fixture
def label_question_payload():
    return {
        "name": "label",
        "description": "label",
        "required": True,
        "labels": ["1", "2"],
    }


@pytest.fixture
def ranking_question_payload():
    return {
        "name": "label",
        "description": "label",
        "required": True,
        "values": ["1", "2"],
    }


@pytest.fixture
def mocked_is_on_huggingface(mocker: "MockerFixture") -> bool:
    mocker.patch(
        "argilla_v1.client.feedback.integrations.huggingface.model_card.model_card.is_on_huggingface", return_value=True
    )


@pytest.fixture
def test_remote_dataset_with_records(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records_with_metadata: List[FeedbackRecord],
    owner: "User",
):
    singleton.init(api_key=owner.api_key)
    ws = Workspace.create(name="test-workspace")

    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="integer-metadata"),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )

    remote = dataset.push_to_argilla(name="test_dataset", workspace=ws)

    remote.add_records(feedback_dataset_records_with_metadata)
    return remote
