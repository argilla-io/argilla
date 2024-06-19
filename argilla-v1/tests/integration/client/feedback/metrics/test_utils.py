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

from typing import TYPE_CHECKING, List, Optional, Union

import pytest
from argilla_v1.client.feedback.dataset import FeedbackDataset
from argilla_v1.client.feedback.metrics.utils import (
    get_responses_and_suggestions_per_user,
    get_unified_responses_and_suggestions,
)
from argilla_v1.client.feedback.schemas import FeedbackRecord

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes


@pytest.mark.parametrize(
    "question, status, num_responses",
    [
        ("question-1", "submitted", 4),
        ("question-2", "submitted", 4),
        ("question-3", "submitted", 4),
        ("question-4", "submitted", 4),
        ("question-5", "submitted", 4),
        ("question-1", "draft", 0),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
def test_responses_and_suggestions_per_user(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records_with_paired_suggestions: List[FeedbackRecord],
    question: str,
    status: str,
    num_responses: int,
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records_with_paired_suggestions)

    responses_and_suggestions_per_user = get_responses_and_suggestions_per_user(
        dataset, question, filter_by={"response_status": status}
    )
    num_users = 3
    if status != "submitted":
        assert len(responses_and_suggestions_per_user) == num_users
    else:
        assert len(responses_and_suggestions_per_user) == num_users
        assert isinstance(responses_and_suggestions_per_user, dict)
        assert all(
            [
                set(user_data.keys()) == {"responses", "suggestions"}
                for user_id, user_data in responses_and_suggestions_per_user.items()
            ]
        )
        user_data = responses_and_suggestions_per_user[list(responses_and_suggestions_per_user.keys())[0]]
        assert len(user_data["responses"]) == len(user_data["suggestions"]) == num_responses


@pytest.mark.parametrize(
    "question, expected_unified_responses, value_type, strategy",
    [
        # TextQuestion
        ("question-1", None, None, None),
        # RatingQuestion
        ("question-2", [1, 1, 1, 2], int, "majority"),
        # LabelQuestion
        ("question-3", [1, 1, 1, 2], str, "majority"),
        # MultiLabelQuestion
        ("question-4", [("a", "c"), ("a", "c"), ("c", "b"), ("b", "c")], tuple, "majority"),
        # RankingQuestion
        # TODO(plaguss): Activate this test when we have a strategy for RankingQuestion (#4295)
        # ("question-5", [1, 1, 1, 2], str, "majority"),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
def test_get_unified_responses_and_suggestions(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records_with_paired_suggestions: List[FeedbackRecord],
    question: str,
    expected_unified_responses: Optional[Union[List, str, int]],
    value_type: type,
    strategy: str,
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records_with_paired_suggestions)

    if question == "question-1":
        with pytest.raises(NotImplementedError, match="^This function is not available"):
            get_unified_responses_and_suggestions(dataset, question)
    else:
        unified_dataset = dataset.compute_unified_responses(question, strategy)
        unified_responses, suggestions = get_unified_responses_and_suggestions(unified_dataset, question)
        assert len(unified_responses) == len(suggestions) == len(expected_unified_responses)
        assert all([isinstance(response, value_type) for response in unified_responses])
