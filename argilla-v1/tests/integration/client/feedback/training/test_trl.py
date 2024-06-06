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

import os
import re
from collections import Counter
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, List

import pytest
from argilla_v1.client.feedback.dataset import FeedbackDataset
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.feedback.training.base import ArgillaTrainer
from argilla_v1.client.feedback.training.schemas.base import (
    TrainingTask,
)
from argilla_v1.client.feedback.training.schemas.return_types import (
    DPOReturnTypes,
    PPOReturnTypes,
    RMReturnTypes,
    SFTReturnTypes,
)
from datasets import Dataset, DatasetDict
from peft import LoraConfig, TaskType
from transformers import AutoModelForCausalLM, AutoModelForSequenceClassification, AutoTokenizer
from trl import AutoModelForCausalLMWithValueHead

from tests.integration.client.feedback.helpers import (
    formatting_func_dpo,
    formatting_func_ppo,
    formatting_func_rm,
    formatting_func_sft,
)
from tests.integration.training.helpers import train_with_cleanup

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes

OUTPUT_DIR = "tmp"
FRAMEWORK = "trl"


def try_wrong_format(dataset, task, format_func: Any) -> None:
    task = task(lambda _: {"test": "test"})
    with pytest.raises(
        ValueError,
        match=re.escape(f"formatting_func must return {format_func.__annotations__['format']}, not <class 'list'>"),
    ):
        trainer = ArgillaTrainer(dataset=dataset, task=task, framework=FRAMEWORK)
        trainer.train(OUTPUT_DIR)


def formatting_func_sft(sample: Dict[str, Any]) -> Iterator[str]:
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

    try_wrong_format(dataset=dataset, task=TrainingTask.for_supervised_fine_tuning, format_func=SFTReturnTypes)

    task = TrainingTask.for_supervised_fine_tuning(formatting_func_sft)
    train_dataset = dataset.prepare_for_training(framework=FRAMEWORK, task=task)
    assert isinstance(train_dataset, Dataset)
    assert len(train_dataset) == 4
    train_dataset_dict = dataset.prepare_for_training(framework=FRAMEWORK, task=task, train_size=0.5)
    assert isinstance(train_dataset_dict, DatasetDict)
    assert tuple(train_dataset_dict.keys()) == ("train", "test")
    assert len(train_dataset_dict["train"]) == 2

    small_model_id = "sshleifer/tiny-gpt2"
    loaded_model = AutoModelForCausalLM.from_pretrained(small_model_id)
    loaded_tokenizer = AutoTokenizer.from_pretrained(small_model_id)
    loaded_tokenizer.pad_token_id = loaded_tokenizer.eos_token_id
    # Set some values to track and assert later
    loaded_model.test_value = 12
    loaded_tokenizer.test_value = 12
    for model, tokenizer in [(small_model_id, None), (loaded_model, loaded_tokenizer)]:
        trainer = ArgillaTrainer(dataset, task, framework=FRAMEWORK, model=model, tokenizer=tokenizer)
        trainer.update_config(max_steps=3)
        assert trainer._trainer.training_args_kwargs["max_steps"] == 3
        trainer.update_config(max_steps=1)
        assert trainer._trainer.training_args_kwargs["max_steps"] == 1
        train_with_cleanup(trainer, OUTPUT_DIR)

        eval_trainer = ArgillaTrainer(dataset, task, framework=FRAMEWORK, model=model, train_size=0.5)
        eval_trainer.update_config(max_steps=1)
        train_with_cleanup(eval_trainer, OUTPUT_DIR)

        # Verify that the passed model and tokenizer are used
        if tokenizer is not None:
            assert trainer._trainer.trainer_model.test_value == 12
            assert trainer._trainer.trainer_tokenizer.test_value == 12


def formatting_func_rm(sample: Dict[str, Any]):
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
            return [(sample["text"], sample["text"][5:10]), (sample["text"], sample["text"][:5])]


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

    try_wrong_format(dataset=dataset, task=TrainingTask.for_reward_modeling, format_func=RMReturnTypes)

    task = TrainingTask.for_reward_modeling(formatting_func_rm)
    train_dataset = dataset.prepare_for_training(framework=FRAMEWORK, task=task)
    assert isinstance(train_dataset, Dataset)
    assert len(train_dataset) == 6
    train_dataset_dict = dataset.prepare_for_training(framework=FRAMEWORK, task=task, train_size=0.5)
    assert isinstance(train_dataset_dict, DatasetDict)
    assert tuple(train_dataset_dict.keys()) == ("train", "test")
    assert len(train_dataset_dict["train"]) == 3

    small_model_id = "sshleifer/tiny-gpt2"
    loaded_model = AutoModelForSequenceClassification.from_pretrained(small_model_id)
    loaded_tokenizer = AutoTokenizer.from_pretrained(small_model_id)
    loaded_tokenizer.pad_token_id = loaded_tokenizer.eos_token_id
    # Set some values to track and assert later
    loaded_model.test_value = 12
    loaded_tokenizer.test_value = 12
    for model, tokenizer in [(small_model_id, None), (loaded_model, loaded_tokenizer)]:
        trainer = ArgillaTrainer(dataset, task, framework=FRAMEWORK, model=model, tokenizer=tokenizer)
        trainer.update_config(max_steps=3)
        assert trainer._trainer.training_args_kwargs["max_steps"] == 3
        trainer.update_config(max_steps=1)
        assert trainer._trainer.training_args_kwargs["max_steps"] == 1
        train_with_cleanup(trainer, OUTPUT_DIR)

        eval_trainer = ArgillaTrainer(
            dataset, task, framework=FRAMEWORK, model=model, tokenizer=tokenizer, train_size=0.5
        )
        eval_trainer.update_config(max_steps=1)
        train_with_cleanup(eval_trainer, OUTPUT_DIR)

        # Verify that the passed model and tokenizer are used
        if tokenizer is not None:
            assert trainer._trainer.trainer_model.test_value == 12
            assert trainer._trainer.trainer_tokenizer.test_value == 12


def formatting_func_ppo(sample: Dict[str, Any]):
    return sample["text"]


@pytest.mark.skip("FAILING BECAUSE: probability tensor contains either `inf`, `nan` or element < 0")
def test_prepare_for_training_ppo(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
) -> None:
    from transformers import pipeline
    from trl import PPOConfig

    reward_model = pipeline("sentiment-analysis", model="lvwerra/distilbert-imdb")
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 2)

    try_wrong_format(dataset=dataset, task=TrainingTask.for_proximal_policy_optimization, format_func=PPOReturnTypes)

    task = TrainingTask.for_proximal_policy_optimization(formatting_func=formatting_func_ppo)
    train_dataset = dataset.prepare_for_training(framework=FRAMEWORK, task=task)
    assert isinstance(train_dataset, Dataset)
    assert len(train_dataset) == 10
    train_dataset_dict = dataset.prepare_for_training(framework=FRAMEWORK, task=task, train_size=0.5)
    assert isinstance(train_dataset_dict, DatasetDict)
    assert tuple(train_dataset_dict.keys()) == ("train", "test")
    assert len(train_dataset_dict["train"]) == 5

    small_model_id = "sshleifer/tiny-gpt2"
    loaded_model = AutoModelForCausalLMWithValueHead.from_pretrained(small_model_id)
    loaded_tokenizer = AutoTokenizer.from_pretrained(small_model_id)
    loaded_tokenizer.pad_token_id = loaded_tokenizer.eos_token_id
    # Set some values to track and assert later
    loaded_model.test_value = 12
    loaded_tokenizer.test_value = 12
    for model, tokenizer in [(small_model_id, None), (loaded_model, loaded_tokenizer)]:
        trainer = ArgillaTrainer(dataset, task, framework=FRAMEWORK, model=model, tokenizer=tokenizer)
        trainer.update_config(config=PPOConfig(batch_size=1, ppo_epochs=1), reward_model=reward_model)
        assert trainer._trainer.trainer_kwargs["config"].batch_size == 1
        trainer.update_config(generation_kwargs={"top_k": 0.0, "top_p": 1.0, "do_sample": True})
        assert trainer._trainer.training_args_kwargs["generation_kwargs"]["top_p"] == 1.0
        train_with_cleanup(trainer, OUTPUT_DIR)

        # Reload the model, as the previous trainer updated it
        if tokenizer is not None:
            model = AutoModelForCausalLMWithValueHead.from_pretrained(small_model_id)

        eval_trainer = ArgillaTrainer(
            dataset, task, framework=FRAMEWORK, model=model, tokenizer=tokenizer, train_size=0.5
        )
        eval_trainer.update_config(config=PPOConfig(batch_size=1, ppo_epochs=1), reward_model=reward_model)
        eval_trainer.update_config(max_steps=1)
        train_with_cleanup(eval_trainer, OUTPUT_DIR)

        # Verify that the passed model and tokenizer are used
        if tokenizer is not None:
            assert trainer._trainer.trainer_model.test_value == 12
            assert trainer._trainer.trainer_tokenizer.test_value == 12


def formatting_func_dpo(sample: Dict[str, Any]):
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
                (sample["text"], sample["text"][::-1], sample["text"][:5]),
                (sample["text"][::-1], sample["text"], sample["text"][:5]),
            ]


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

    try_wrong_format(dataset=dataset, task=TrainingTask.for_direct_preference_optimization, format_func=DPOReturnTypes)

    task = TrainingTask.for_direct_preference_optimization(formatting_func_dpo)
    train_dataset = dataset.prepare_for_training(framework=FRAMEWORK, task=task)
    assert isinstance(train_dataset, Dataset)
    assert len(train_dataset) == 6
    train_dataset_dict = dataset.prepare_for_training(framework=FRAMEWORK, task=task, train_size=0.5)
    assert isinstance(train_dataset_dict, DatasetDict)
    assert tuple(train_dataset_dict.keys()) == ("train", "test")
    assert len(train_dataset_dict["train"]) == 3

    small_model_id = "sshleifer/tiny-gpt2"
    loaded_model = AutoModelForCausalLM.from_pretrained(small_model_id)
    loaded_tokenizer = AutoTokenizer.from_pretrained(small_model_id)
    loaded_tokenizer.pad_token_id = loaded_tokenizer.eos_token_id
    # Set some values to track and assert later
    loaded_model.test_value = 12
    loaded_tokenizer.test_value = 12
    for model, tokenizer in [(small_model_id, None), (loaded_model, loaded_tokenizer)]:
        trainer = ArgillaTrainer(dataset, task, framework=FRAMEWORK, model=model, tokenizer=tokenizer)
        trainer.update_config(max_steps=3)
        assert trainer._trainer.training_args_kwargs["max_steps"] == 3
        trainer.update_config(max_steps=1)
        assert trainer._trainer.training_args_kwargs["max_steps"] == 1
        train_with_cleanup(trainer, OUTPUT_DIR)

        eval_trainer = ArgillaTrainer(
            dataset, task, framework=FRAMEWORK, model=model, tokenizer=tokenizer, train_size=0.5
        )
        eval_trainer.update_config(max_steps=1)
        train_with_cleanup(eval_trainer, OUTPUT_DIR)

        # Verify that the passed model and tokenizer are used
        if tokenizer is not None:
            assert trainer._trainer.trainer_model.test_value == 12
            assert trainer._trainer.trainer_tokenizer.test_value == 12


@pytest.mark.skip("FAILING BECAUSE: probability tensor contains either `inf`, `nan` or element < 0")
def test_sft_with_peft(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
    tmp_path,
) -> None:
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 2)

    task = TrainingTask.for_supervised_fine_tuning(formatting_func_sft)

    small_model_id = "sshleifer/tiny-gpt2"
    loaded_model = AutoModelForCausalLM.from_pretrained(small_model_id)
    loaded_tokenizer = AutoTokenizer.from_pretrained(small_model_id)
    loaded_tokenizer.pad_token_id = loaded_tokenizer.eos_token_id
    trainer = ArgillaTrainer(dataset, task, framework=FRAMEWORK, model=loaded_model, tokenizer=loaded_tokenizer)
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,  # 32,
    )
    trainer.update_config(peft_config=peft_config)
    trainer.train(tmp_path)
    assert "adapter_config.json" in os.listdir(tmp_path)
    assert "adapter_model.bin" in os.listdir(tmp_path)


# @pytest.mark.slow
@pytest.mark.skip("FAILING BECAUSE: probability tensor contains either `inf`, `nan` or element < 0")
@pytest.mark.parametrize(
    "formatting_func, training_task",
    (
        (formatting_func_sft, TrainingTask.for_supervised_fine_tuning),
        (formatting_func_rm, TrainingTask.for_reward_modeling),
        (formatting_func_ppo, TrainingTask.for_proximal_policy_optimization),
        (formatting_func_dpo, TrainingTask.for_direct_preference_optimization),
    ),
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_push_to_huggingface(
    formatting_func: Callable,
    training_task: Callable,
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
    mocked_trainer_push_to_huggingface,
) -> None:
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 2)

    task = training_task(formatting_func)
    model = "sshleifer/tiny-gpt2"

    trainer = ArgillaTrainer(dataset=dataset, task=task, framework="trl", model=model)

    if training_task == TrainingTask.for_proximal_policy_optimization:
        from transformers import pipeline
        from trl import PPOConfig

        reward_model = pipeline("sentiment-analysis", model="lvwerra/distilbert-imdb")
        trainer.update_config(config=PPOConfig(batch_size=1, ppo_epochs=2), reward_model=reward_model)
    else:
        trainer.update_config(max_steps=1)

    train_with_cleanup(trainer, OUTPUT_DIR)

    trainer.push_to_huggingface("mocked", generate_card=False)
