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

import uuid
from typing import TYPE_CHECKING, List, Union

import pytest
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.metrics.agreement_metrics import (
    AgreementMetric,
    AgreementMetricResult,
    prepare_dataset_for_annotation_task,
)
from argilla.client.feedback.schemas import FeedbackRecord

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes


@pytest.mark.parametrize(
    "question, num_items",
    [
        ("question-1", None),
        ("question-2", 12),
        ("question-3", 12),
        ("question-4", 12),
        ("question-5", 12),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
def test_prepare_dataset_for_annotation_task(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records_with_paired_suggestions: List[FeedbackRecord],
    question: str,
    num_items: int,
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records_with_paired_suggestions)

    if question in ("question-1",):
        with pytest.raises(NotImplementedError, match=r"^Question '"):
            prepare_dataset_for_annotation_task(dataset, question)
    else:
        formatted_dataset = prepare_dataset_for_annotation_task(dataset, question)
        assert isinstance(formatted_dataset, list)
        assert len(formatted_dataset) == num_items
        item = formatted_dataset[0]
        assert isinstance(item, tuple)
        assert isinstance(item[0], str)
        assert item[0].startswith("00000000-")  # beginning of our uuid for tests
        assert isinstance(item[1], str)
        assert item[1].startswith("question-")
        assert isinstance(item[2], (int, str))


@pytest.mark.parametrize(
    "question, metric_names",
    [
        # TextQuestion
        ("question-1", None),
        # RatingQuestion
        ("question-2", "alpha"),
        ("question-2", ["alpha"]),
        # LabelQuestion
        ("question-3", "alpha"),
        # MultiLabelQuestion
        ("question-4", "alpha"),
        # RankingQuestion
        ("question-5", "alpha"),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
def test_agreement_metrics(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records_with_paired_suggestions: List[FeedbackRecord],
    question: str,
    metric_names: Union[str, List[str]],
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records_with_paired_suggestions)

    if question in ("question-1",):
        with pytest.raises(NotImplementedError, match=r"^No metrics are defined currently for"):
            AgreementMetric(dataset=dataset, question_name=question)
    else:
        metric = AgreementMetric(dataset=dataset, question_name=question)
        metrics_report = metric.compute(metric_names)
        assert isinstance(metrics_report, list)
        assert all([isinstance(m, AgreementMetricResult) for m in metrics_report])
