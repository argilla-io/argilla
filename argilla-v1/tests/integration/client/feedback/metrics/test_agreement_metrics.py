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
from typing import TYPE_CHECKING, FrozenSet, List, Tuple, Union

import pytest
from argilla_v1 import User, init
from argilla_v1.client.feedback.dataset import FeedbackDataset
from argilla_v1.client.feedback.metrics.agreement_metrics import (
    AgreementMetric,
    AgreementMetricResult,
    prepare_dataset_for_annotation_task,
)
from argilla_v1.client.feedback.schemas import FeedbackRecord

from tests.factories import UserFactory, WorkspaceFactory

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes


@pytest.mark.parametrize(
    "question, metric_names",
    [
        # RatingQuestion
        ("question-2", {"alpha"}),
        # LabelQuestion
        ("question-3", {"alpha"}),
        # MultiLabelQuestion
        ("question-4", {"alpha"}),
        # RankingQuestion
        ("question-5", {"alpha"}),
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

    metric = AgreementMetric(
        dataset=dataset, question_name=question, field_name=[field.name for field in feedback_dataset_fields]
    )
    assert set(metric.allowed_metrics) == metric_names


@pytest.mark.parametrize(
    "field, question, num_items, type_of_data",
    [
        (["text"], "question-1", None, None),
        (["text", "label"], "question-2", 12, int),
        (["text", "label"], "question-3", 12, str),
        (["text"], "question-4", 12, FrozenSet),
        (["label"], "question-5", 12, Tuple),
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
    field: Union[str, List[str]],
    num_items: int,
    type_of_data: Union[str, int, FrozenSet, Tuple[str]],
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records_with_paired_suggestions)

    if question == "question-1":
        with pytest.raises(NotImplementedError, match=r"^Question '"):
            prepare_dataset_for_annotation_task(dataset, question, field)
    else:
        formatted_dataset = prepare_dataset_for_annotation_task(dataset, question, field)
        assert isinstance(formatted_dataset, list)
        assert len(formatted_dataset) == num_items
        item = formatted_dataset[0]
        assert isinstance(item, tuple)
        assert isinstance(item[0], str)
        assert item[0].startswith("00000000-")  # beginning of our uuid for tests
        assert isinstance(item[1], str)
        expected_field_value = (
            " ".join([feedback_dataset_records_with_paired_suggestions[0].fields[f] for f in field])
            if isinstance(field, list)
            else feedback_dataset_records_with_paired_suggestions[0].fields[field]
        )
        assert item[1] == expected_field_value
        assert isinstance(item[2], type_of_data)


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
            AgreementMetric(
                dataset=dataset,
                question_name=question,
                field_name=[field.name for field in feedback_dataset_fields],
            )
    else:
        metric = AgreementMetric(
            dataset=dataset,
            question_name=question,
            field_name=[field.name for field in feedback_dataset_fields],
        )
        # Test for repr method
        assert repr(metric) == f"AgreementMetric(question_name={question})"
        metrics_report = metric.compute(metric_names)
        if isinstance(metric_names, str):
            metrics_report = [metrics_report]
        elif isinstance(metric_names, list):
            if len(metric_names) == 1:
                metrics_report = [metrics_report]
        assert isinstance(metrics_report, list)
        assert all([isinstance(m, AgreementMetricResult) for m in metrics_report])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field, question, metric_names",
    [
        # TextQuestion
        (["text"], "question-1", None),
        # RatingQuestion
        (["text", "label"], "question-2", "alpha"),
        (["text", "label"], "question-2", ["alpha"]),
        # LabelQuestion
        ("text", "question-3", "alpha"),
        # MultiLabelQuestion
        ("label", "question-4", "alpha"),
        # RankingQuestion
        (["text", "label"], "question-5", "alpha"),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
async def test_agreement_metrics_remote(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records_with_paired_suggestions: List[FeedbackRecord],
    question: str,
    field: Union[str, List[str]],
    metric_names: Union[str, List[str]],
    owner: User,
):
    init(api_key=owner.api_key)
    workspace = await WorkspaceFactory.create(name="test_workspace")
    # Add the 4 users for the sample dataset
    for i in range(1, 4):
        await UserFactory.create(username=f"test_user{i}", id=uuid.UUID(int=i))

    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records_with_paired_suggestions)
    remote = dataset.push_to_argilla(name="test-metrics", workspace=workspace.name)

    if question in ("question-1",):
        with pytest.raises(NotImplementedError, match=r"^No metrics are defined currently for"):
            AgreementMetric(
                dataset=remote,
                question_name=question,
                field_name=field,
            )
    else:
        metric = AgreementMetric(
            dataset=remote,
            question_name=question,
            field_name=field,
        )
        # Test for repr method
        assert repr(metric) == f"AgreementMetric(question_name={question})"
        metrics_report = metric.compute(metric_names)
        if isinstance(metric_names, str):
            metrics_report = [metrics_report]
        elif isinstance(metric_names, list):
            if len(metric_names) == 1:
                metrics_report = [metrics_report]
        assert isinstance(metrics_report, list)
        assert all([isinstance(m, AgreementMetricResult) for m in metrics_report])


@pytest.mark.parametrize(
    "field, question, metric_names",
    [
        # TextQuestion
        (["text"], "question-1", None),
        # RatingQuestion
        (["text", "label"], "question-2", "alpha"),
        (["text", "label"], "question-2", ["alpha"]),
        # LabelQuestion
        ("text", "question-3", "alpha"),
        # MultiLabelQuestion
        ("label", "question-4", "alpha"),
        # RankingQuestion
        (["text", "label"], "question-5", "alpha"),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
def test_agreement_metrics_from_feedback_dataset(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records_with_paired_suggestions: List[FeedbackRecord],
    question: str,
    field: Union[str, List[str]],
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
            dataset.compute_agreement_metrics(question_name=question, field_name=field, metric_names=metric_names)
    else:
        metrics_report = dataset.compute_agreement_metrics(
            question_name=question, field_name=field, metric_names=metric_names
        )

        if isinstance(metric_names, str):
            metrics_report = [metrics_report]
        elif isinstance(metric_names, list):
            if len(metric_names) == 1:
                metrics_report = [metrics_report]
        assert isinstance(metrics_report, list)
        assert all([isinstance(m, AgreementMetricResult) for m in metrics_report])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field, question, metric_names",
    [
        # TextQuestion
        (["text"], "question-1", None),
        # RatingQuestion
        (["text", "label"], "question-2", "alpha"),
        (["text", "label"], "question-2", ["alpha"]),
        # LabelQuestion
        ("text", "question-3", "alpha"),
        # MultiLabelQuestion
        ("label", "question-4", "alpha"),
        # RankingQuestion
        (["text", "label"], "question-5", "alpha"),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
async def test_agreement_metrics_from_remote_feedback_dataset(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records_with_paired_suggestions: List[FeedbackRecord],
    question: str,
    field: Union[str, List[str]],
    metric_names: Union[str, List[str]],
    owner: User,
) -> None:
    init(api_key=owner.api_key)
    workspace = await WorkspaceFactory.create(name="test_workspace")
    # Add the 4 users for the sample dataset
    for i in range(1, 4):
        await UserFactory.create(username=f"test_user{i}", id=uuid.UUID(int=i))

    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records_with_paired_suggestions)

    remote = dataset.push_to_argilla(name="test-metrics", workspace=workspace.name)

    if question in ("question-1",):
        with pytest.raises(NotImplementedError, match=r"^No metrics are defined currently for"):
            remote.compute_agreement_metrics(question_name=question, field_name=field, metric_names=metric_names)
    else:
        metrics_report = remote.compute_agreement_metrics(
            question_name=question, field_name=field, metric_names=metric_names
        )

        if isinstance(metric_names, str):
            metrics_report = [metrics_report]
        elif isinstance(metric_names, list):
            if len(metric_names) == 1:
                metrics_report = [metrics_report]
        assert isinstance(metrics_report, list)
        assert all([isinstance(m, AgreementMetricResult) for m in metrics_report])
