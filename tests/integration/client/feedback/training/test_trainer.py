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

from typing import TYPE_CHECKING, List, Union

import pytest

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes

import shutil
import sys
from pathlib import Path

from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
)
from argilla.client.feedback.training import ArgillaTrainer
from argilla.client.feedback.training.schemas import (
    TrainingTask,
    TrainingTaskForTextClassification,
    TrainingTaskMapping,
    TrainingTaskMappingForTextClassification,
)
from argilla.client.feedback.unification import LabelQuestionUnification
from argilla.client.models import Framework

__OUTPUT_DIR__ = "tmp"


@pytest.mark.parametrize(
    "framework",
    [
        # Framework("spacy"),
        # Framework("spacy-transformers"),
        Framework("transformers"),
        Framework("spark-nlp"),
        Framework("span_marker"),
        Framework("setfit"),
        Framework("peft"),
        Framework("spark-nlp"),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_prepare_for_training_text_classification(
    framework: Union[Framework, str],
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
) -> None:
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 5)

    questions = [
        question for question in dataset.questions if isinstance(question, (LabelQuestion, MultiLabelQuestion))
    ]
    label = LabelQuestionUnification(question=questions[0])
    task = TrainingTask.for_text_classification(text=dataset.fields[0], label=label)

    if framework == Framework("span_marker"):
        with pytest.raises(
            NotImplementedError,
            match=f"Framework {framework} is not supported for this {TrainingTaskForTextClassification}.",
        ):
            trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework, fetch_records=False)
    elif framework == Framework("spark-nlp"):
        with pytest.raises(NotImplementedError, match=f"{framework} is not a valid framework."):
            trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework, fetch_records=False)
    else:
        if framework in [Framework("peft")] and sys.version_info < (3, 9):
            pass
        else:
            trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework, fetch_records=False)
            if framework in [Framework("spacy"), Framework("spacy-transformers")]:
                trainer.update_config(max_steps=1)
            elif framework in [Framework("transformers"), Framework("setfit")]:
                trainer.update_config(num_iterations=1)
            trainer.train(__OUTPUT_DIR__)

    if Path(__OUTPUT_DIR__).exists():
        shutil.rmtree(__OUTPUT_DIR__)


@pytest.mark.parametrize(
    "callable",
    (
        lambda: TrainingTaskMapping.for_text_classification(None, None),
        lambda: TrainingTaskMapping.for_direct_preference_optimization(None),
        lambda: TrainingTaskMapping.for_reward_modelling(None),
        lambda: TrainingTaskMapping.for_supervised_fine_tuning(None),
    ),
)
def test_deprecations(callable) -> None:
    with pytest.warns(DeprecationWarning, match="`TrainingTaskMapping` has been renamed to `TrainingTask`"):
        # This'll crash because we're passing None, but we only test the warning
        try:
            callable()
        except:
            pass


def test_deprecations_for_text_classification():
    with pytest.warns(
        DeprecationWarning,
        match="`TrainingTaskMappingForTextClassification` has been renamed to `TrainingTaskForTextClassification`",
    ):
        # This'll crash because we're passing None, but we only test the warning
        try:
            TrainingTaskMappingForTextClassification(None)
        except:
            pass
