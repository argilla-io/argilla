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
from argilla.client.feedback.integrations.huggingface.card import (
    ArgillaDatasetCard,
    size_categories_parser,
)
from huggingface_hub import DatasetCardData

if TYPE_CHECKING:
    from argilla.client.feedback.schemas import FeedbackRecord
    from argilla.client.feedback.types import AllowedFieldTypes, AllowedQuestionTypes
    from datasets import Dataset


@pytest.mark.parametrize(
    "size,expected",
    [
        (1, "n<1K"),
        (999, "n<1K"),
        (1_000, "1K<n<10K"),
        (10_000_000_000_001, "n>1T"),
    ],
)
def test_size_categories_parser(size: int, expected: str) -> None:
    assert size_categories_parser(size) == expected


@pytest.mark.usefixtures(
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_guidelines",
    "feedback_dataset_records",
    "feedback_dataset_huggingface",
)
def test_argilla_dataset_card_from_template(
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_guidelines: str,
    feedback_dataset_records: List["FeedbackRecord"],
    feedback_dataset_huggingface: "Dataset",
) -> None:
    card = ArgillaDatasetCard.from_template(
        card_data=DatasetCardData(language="en", size_categories="n<1K", tags=["rlfh", "argilla", "human-feedback"]),
        template_path=ArgillaDatasetCard.default_template_path,
        repo_id="argilla/dataset-card",
        argilla_fields=feedback_dataset_fields,
        argilla_questions=feedback_dataset_questions,
        argilla_guidelines=feedback_dataset_guidelines,
        argilla_record=feedback_dataset_records[0].dict(),
        huggingface_record=feedback_dataset_huggingface[0],
    )

    assert isinstance(card, ArgillaDatasetCard)
    assert card.default_template_path == ArgillaDatasetCard.default_template_path
    assert card.content.__contains__("# Dataset Card for dataset-card")
