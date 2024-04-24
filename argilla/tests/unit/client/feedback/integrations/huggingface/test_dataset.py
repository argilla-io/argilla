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

from typing import Any, Dict

import pytest
from argilla.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla.client.feedback.integrations.huggingface.dataset import HuggingFaceDatasetMixin
from argilla.client.feedback.schemas.fields import TextField
from argilla.client.feedback.schemas.questions import TextQuestion
from argilla.client.feedback.schemas.records import FeedbackRecord


class TestSuiteHuggingFaceDatasetMixin:
    @pytest.mark.parametrize(
        "record, hf_record",
        [
            (FeedbackRecord(fields={"required-field": "value"}), {"required-field": "value", "optional-field": None}),
            (
                FeedbackRecord(fields={"required-field": "value", "optional-field": "value"}),
                {"required-field": "value", "optional-field": "value"},
            ),
        ],
    )
    def test__huggingface_format(self, record: FeedbackRecord, hf_record: Dict[str, Any]) -> None:
        dataset = FeedbackDataset(
            fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
            questions=[TextQuestion(name="question", required=True)],
        )
        dataset.add_records([record])

        hf_dataset = HuggingFaceDatasetMixin._huggingface_format(dataset=dataset)
        assert all(field.name in hf_dataset.features for field in dataset.fields)
        assert hf_record == {
            key: value for key, value in hf_dataset[0].items() if key in [field.name for field in dataset.fields]
        }
