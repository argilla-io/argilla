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
from argilla.client.feedback.metrics.annotator_metrics import AnnotatorMetric, UnifiedAnnotatorMetric
from argilla.client.feedback.metrics.base import AnnotatorMetricResult
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
)
from argilla.client.feedback.unification import (
    LabelQuestionStrategy,
    LabelQuestionUnification,
    MultiLabelQuestionStrategy,
    MultiLabelQuestionUnification,
    RankingQuestionStrategy,
    RankingQuestionUnification,
    RatingQuestionStrategy,
    RatingQuestionUnification,
    UnifiedValueSchema,
)

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes


@pytest.mark.parametrize(
    "question, metric_names",
    [
        # TextQuestion
        ("question-1", ["gleu"]),
        # RatingQuestion
        ("question-2", "accuracy"),
        ("question-2", ["accuracy", "f1-score", "precision", "recall", "confusion-matrix", "spearman-r"]),
        # LabelQuestion
        ("question-3", "accuracy"),
        ("question-3", ["accuracy", "f1-score", "precision", "recall", "confusion-matrix", "pearson-r"]),
        # No current implementation for MultiLabelQuestion
        ("question-4", "accuracy"),
        # RankingQuestion
        ("question-5", "accuracy"),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
def test_annotator_metric(
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

    if question in ("question-4", "question-5"):
        with pytest.raises(NotImplementedError):
            AnnotatorMetric(dataset, question)
    else:
        metric = AnnotatorMetric(dataset, question)
        metrics_report = metric.compute(metric_names)
        assert len(metrics_report) == 3  # Number of annotators
        assert isinstance(metrics_report, dict)
        user_id = str(uuid.UUID(int=1))
        metric_results = metrics_report[user_id]
        assert isinstance(metric_results, list)
        metric_result = metric_results[0]
        assert isinstance(metric_result, AnnotatorMetricResult)
        if isinstance(metric_names, str):
            metric_names = [metric_names]

        assert all([result.metric_name == name for result, name in zip(metric_results, metric_names)])


@pytest.mark.parametrize(
    "question, metric_names, strategy_name",
    [
        # TextQuestion
        ("question-1", None, None),
        # RatingQuestion
        ("question-2", "accuracy", "majority"),
        ("question-2", ["accuracy", "f1-score", "precision", "recall", "confusion-matrix", "spearman-r"], "majority"),
        # LabelQuestion
        ("question-3", ["accuracy", "f1-score", "precision", "recall", "confusion-matrix", "pearson-r"], "majority"),
        # MultiLabelQuestion
        ("question-4", None, None),
        # RankingQuestion
        ("question-5", None, None),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
def test_annotator_metrics_unified(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records_with_paired_suggestions: List[FeedbackRecord],
    question: str,
    metric_names: Union[str, List[str]],
    strategy_name: str,
):
    if not strategy_name:
        return
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records_with_paired_suggestions)

    unified_dataset = dataset.unify_responses(question, strategy_name)

    if question in ("question-1", "question-4", "question-5"):
        with pytest.raises(NotImplementedError):
            UnifiedAnnotatorMetric(unified_dataset, question)
    else:
        metric = UnifiedAnnotatorMetric(unified_dataset, question)
        metrics_report = metric.compute(metric_names)

        if isinstance(metric_names, list):
            assert isinstance(metrics_report, list)
        else:
            assert isinstance(metrics_report, AnnotatorMetricResult)
            metrics_report = [metrics_report]
            metric_names = [metric_names]

        assert all([result.metric_name == name for result, name in zip(metrics_report, metric_names)])


@pytest.mark.parametrize(
    "question, metric_names",
    [
        # TextQuestion
        ("question-1", {"gleu", "rouge"}),
        # RatingQuestion
        ("question-2", {"accuracy", "f1-score", "precision", "recall", "confusion-matrix", "spearman-r"}),
        # LabelQuestion
        ("question-3", {"accuracy", "f1-score", "precision", "recall", "confusion-matrix", "pearson-r"}),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
def test_allowed_metrics(
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

    metric = AnnotatorMetric(dataset, question)
    assert set(metric.allowed_metrics) == metric_names
