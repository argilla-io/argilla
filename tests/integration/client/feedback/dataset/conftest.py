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
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.schemas.fields import TextField
from argilla.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla.client.feedback.schemas.questions import TextQuestion
from argilla.client.feedback.schemas.records import FeedbackRecord


@pytest.fixture()
def test_dataset():
    dataset = FeedbackDataset(
        fields=[TextField(name="text")],
        questions=[TextQuestion(name="question")],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="integer-metadata"),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )
    return dataset


@pytest.fixture()
def test_dataset_with_records(test_dataset):
    for metadata in (
        {"terms-metadata": "a", "integer-metadata": 2, "float-metadata": 2.0},
        {"terms-metadata": "a", "integer-metadata": 4, "float-metadata": 4.0},
        {"terms-metadata": "b", "integer-metadata": 4, "float-metadata": 4.0},
        {"terms-metadata": "b", "integer-metadata": 5, "float-metadata": 4.0},
        {"terms-metadata": "c", "integer-metadata": 6, "float-metadata": 6.0},
    ):
        test_dataset.add_records([FeedbackRecord(fields={"text": "text"}, metadata=metadata) for _ in range(2)])
    return test_dataset
