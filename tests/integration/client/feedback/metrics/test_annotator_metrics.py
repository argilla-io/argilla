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
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
)

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes


from sklearn.metrics import accuracy_score


@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records_with_paired_suggestions",
)
def test_metrics_dataset(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records_with_paired_suggestions: List[FeedbackRecord],
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records_with_paired_suggestions)

    df = dataset.format_as("datasets").to_pandas()
    print("DATAFRAME", dataset.format_as("datasets"))
    print("******** DF *")
    print(df[["text", "label", "question-1", "question-1-suggestion"]])
    print("*********")
    # print(df.columns)
    print("*********")
    # print(df["question-1"])
    print(df["question-2"])
    print(df["question-2-suggestion"])
    # print(df["question-3"])
    # print(df["question-4"])
    # print(df["question-5"])
    dfq2 = df["question-2"].apply(lambda x: x[0]["value"])
    print(dfq2)
    acc = accuracy_score(dfq2, df["question-2-suggestion"])
    print(acc)
    assert 1 == 2
