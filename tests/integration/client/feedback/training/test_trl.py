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

from collections import Counter
from typing import TYPE_CHECKING, Any, Dict, Iterator, List

import pytest
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.schemas.records import FeedbackRecord
from argilla.client.feedback.training.base import ArgillaTrainer
from argilla.client.feedback.training.schemas import TrainingTask
from datasets import Dataset, DatasetDict

from tests.integration.training.helpers import train_with_cleanup

if TYPE_CHECKING:
    from argilla.client.feedback.types import AllowedFieldTypes, AllowedQuestionTypes


@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_prepare_for_training_sft(
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
    dataset.add_records(records=feedback_dataset_records * 2)

    def formatting_func(sample: Dict[str, Any]) -> Iterator[str]:
        # For example, the sample must be most frequently rated as "1" in question-2 and
        # label "b" from "question-3" must have not been set by any annotator
        ratings = [
            annotation["value"]
            for annotation in sample["question-2"]
            if annotation["status"] == "submitted" and annotation["value"] is not None
        ]
        labels = [
            annotation["value"]
            for annotation in sample["question-3"]
            if annotation["status"] == "submitted" and annotation["value"] is not None
        ]
        if ratings and Counter(ratings).most_common(1)[0][0] == 1 and "b" not in labels:
            return f"### Text\n{sample['text']}"
        return None

    task = TrainingTask.for_supervised_fine_tuning(formatting_func)
    train_dataset = dataset.prepare_for_training(framework="trl", task=task, fetch_records=False)
    assert isinstance(train_dataset, Dataset)
    assert len(train_dataset) == 6
    train_dataset_dict = dataset.prepare_for_training(framework="trl", task=task, fetch_records=False, train_size=0.5)
    assert isinstance(train_dataset_dict, DatasetDict)
    assert tuple(train_dataset_dict.keys()) == ("train", "test")
    assert len(train_dataset_dict["train"]) == 3

    trainer = ArgillaTrainer(dataset, task, framework="trl", model="sshleifer/tiny-gpt2", fetch_records=False)
    trainer.update_config(max_steps=3)
    assert trainer._trainer.training_args_kwargs["max_steps"] == 3
    trainer.update_config(max_steps=1)
    assert trainer._trainer.training_args_kwargs["max_steps"] == 1
    train_with_cleanup(trainer, "tmp_trl_dir")

    eval_trainer = ArgillaTrainer(
        dataset, task, framework="trl", model="sshleifer/tiny-gpt2", fetch_records=False, train_size=0.5
    )
    eval_trainer.update_config(max_steps=1)
    train_with_cleanup(eval_trainer, "tmp_trl_dir")


@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_prepare_for_training_rm(
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
    dataset.add_records(records=feedback_dataset_records * 2)

    def chosen_rejected_func(sample: Dict[str, Any]):
        # The FeedbackDataset isn't really set up for RM, so we'll just use an arbitrary example here
        labels = [
            annotation["value"]
            for annotation in sample["question-3"]
            if annotation["status"] == "submitted" and annotation["value"] is not None
        ]
        if labels:
            # Three cases for the tests: None, one tuple and yielding multiple tuples
            if labels[0] == "a":
                return None
            elif labels[0] == "b":
                return sample["text"], sample["text"][:5]
            elif labels[0] == "c":
                return [(sample["text"], sample["text"][:5]), (sample["text"], sample["text"][:5])]

    task = TrainingTask.for_reward_modelling(chosen_rejected_func)
    train_dataset = dataset.prepare_for_training(framework="trl", task=task, fetch_records=False)
    assert isinstance(train_dataset, Dataset)
    assert len(train_dataset) == 6
    train_dataset_dict = dataset.prepare_for_training(framework="trl", task=task, fetch_records=False, train_size=0.5)
    assert isinstance(train_dataset_dict, DatasetDict)
    assert tuple(train_dataset_dict.keys()) == ("train", "test")
    assert len(train_dataset_dict["train"]) == 3

    trainer = ArgillaTrainer(dataset, task, framework="trl", model="sshleifer/tiny-gpt2", fetch_records=False)
    trainer.update_config(max_steps=3)
    assert trainer._trainer.training_args_kwargs["max_steps"] == 3
    trainer.update_config(max_steps=1)
    assert trainer._trainer.training_args_kwargs["max_steps"] == 1
    train_with_cleanup(trainer, "tmp_trl_dir")

    eval_trainer = ArgillaTrainer(
        dataset, task, framework="trl", model="sshleifer/tiny-gpt2", fetch_records=False, train_size=0.5
    )
    eval_trainer.update_config(max_steps=1)
    train_with_cleanup(eval_trainer, "tmp_trl_dir")


@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_prepare_for_training_dpo(
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
    dataset.add_records(records=feedback_dataset_records * 2)

    def prompt_chosen_rejected_func(sample: Dict[str, Any]):
        # The FeedbackDataset isn't really set up for DPO, so we'll just use an arbitrary example here
        labels = [
            annotation["value"]
            for annotation in sample["question-3"]
            if annotation["status"] == "submitted" and annotation["value"] is not None
        ]
        if labels:
            # Three cases for the tests: None, one tuple and yielding multiple tuples
            if labels[0] == "a":
                return None
            elif labels[0] == "b":
                return sample["text"][::-1], sample["text"], sample["text"][:5]
            elif labels[0] == "c":
                return [
                    (sample["text"][::-1], sample["text"], sample["text"][:5]),
                    (sample["text"][::-1], sample["text"], sample["text"][:5]),
                ]

    task = TrainingTask.for_direct_preference_optimization(prompt_chosen_rejected_func)
    train_dataset = dataset.prepare_for_training(framework="trl", task=task, fetch_records=False)
    assert isinstance(train_dataset, Dataset)
    assert len(train_dataset) == 6
    train_dataset_dict = dataset.prepare_for_training(framework="trl", task=task, fetch_records=False, train_size=0.5)
    assert isinstance(train_dataset_dict, DatasetDict)
    assert tuple(train_dataset_dict.keys()) == ("train", "test")
    assert len(train_dataset_dict["train"]) == 3

    trainer = ArgillaTrainer(dataset, task, framework="trl", model="sshleifer/tiny-gpt2", fetch_records=False)
    trainer.update_config(max_steps=3)
    assert trainer._trainer.training_args_kwargs["max_steps"] == 3
    trainer.update_config(max_steps=1)
    assert trainer._trainer.training_args_kwargs["max_steps"] == 1
    train_with_cleanup(trainer, "tmp_trl_dir")

    eval_trainer = ArgillaTrainer(
        dataset, task, framework="trl", model="sshleifer/tiny-gpt2", fetch_records=False, train_size=0.5
    )
    eval_trainer.update_config(max_steps=1)
    train_with_cleanup(eval_trainer, "tmp_trl_dir")
