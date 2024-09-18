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
from argilla_v1.client.feedback.schemas.fields import TextField
from argilla_v1.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla_v1.client.feedback.schemas.questions import TextQuestion

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import (
        AllowedFieldTypes,
        AllowedMetadataPropertyTypes,
        AllowedQuestionTypes,
    )


@pytest.fixture
def rating_question_payload() -> dict:
    return {
        "name": "label",
        "description": "label",
        "required": True,
        "values": ["1", "2"],
    }


@pytest.fixture
def label_question_payload() -> dict:
    return {
        "name": "label",
        "description": "label",
        "required": True,
        "labels": ["1", "2"],
    }


@pytest.fixture
def ranking_question_payload() -> dict:
    return {
        "name": "label",
        "description": "label",
        "required": True,
        "values": ["1", "2"],
    }


@pytest.fixture
def feedback_dataset_guidelines() -> str:
    return "guidelines"


@pytest.fixture
def feedback_dataset_fields() -> List["AllowedFieldTypes"]:
    return [
        TextField(name="text-field", required=True),
    ]


@pytest.fixture
def feedback_dataset_questions() -> List["AllowedQuestionTypes"]:
    return [
        TextQuestion(name="text-question", description="text", required=True),
    ]


@pytest.fixture
def feedback_dataset_metadata_properties() -> List["AllowedMetadataPropertyTypes"]:
    return [
        TermsMetadataProperty(name="terms-metadata", values=["1", "2"]),
        IntegerMetadataProperty(name="integer-metadata", min=0, max=10),
        FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
    ]
