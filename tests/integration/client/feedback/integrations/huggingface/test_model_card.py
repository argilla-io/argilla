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
"""Only a subset of the possibilities is tested for speed.
- sentence-transformers with formatting_func.
- transformers with formatting_func.
- transformers with formatting_func.
- transformers with formatting_func.
- transformers with formatting_func.
"""

import shutil
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, List, Union

import pytest
from argilla.client.feedback.integrations.huggingface.card.model_card import (
    _prepare_dict_for_comparison,
    _updated_arguments,
)
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
)
from argilla.client.feedback.unification import LabelQuestionUnification
from argilla.client.models import Framework
from argilla.feedback import ArgillaTrainer, FeedbackDataset, TrainingTask
from argilla.training.utils import get_default_args
from transformers import TrainingArguments

from tests.integration.client.feedback.integrations.huggingface import model_card_checks as patterns
from tests.integration.training.helpers import train_with_cleanup

if TYPE_CHECKING:
    from argilla.client.feedback.schemas import FeedbackRecord
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes


OUTPUT_DIR = "tmp"
DATASET_NAME = "argilla/emotion"


@pytest.mark.parametrize(
    "framework, task_type",
    [
        (Framework("spacy"), "for_text_classification"),
        (Framework("spacy-transformers"), "for_text_classification"),
        (Framework("transformers"), "for_text_classification"),
        (Framework("transformers"), "for_question_answering"),
        (Framework("setfit"), "for_text_classification"),
        (Framework("peft"), "for_text_classification"),
        (Framework("span_marker"), "for_text_classification"),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_model_card_with_defaults(
    framework: Union[Framework, str],
    task_type: str,
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
) -> None:
    # This test is almost a copy from the one in `test_trainer.py`, it's separated for
    # simplicity, but for speed we should test this at the same trainer.

    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 2)

    questions = [
        question for question in dataset.questions if isinstance(question, (LabelQuestion, MultiLabelQuestion))
    ]
    label = LabelQuestionUnification(question=questions[0])

    if task_type == "for_question_answering":
        task = TrainingTask.for_question_answering(
            question=dataset.field_by_name("label"),
            context=dataset.field_by_name("text"),
            answer=dataset.question_by_name("question-1"),
        )
    elif task_type == "for_text_classification":
        task = TrainingTask.for_text_classification(text=dataset.fields[0], label=label)

    if framework == Framework("spacy"):
        model = "en_core_web_sm"
    elif framework == Framework("setfit"):
        model = "all-MiniLM-L6-v2"
    else:
        model = "prajjwal1/bert-tiny"

    if framework == Framework("span_marker"):
        with pytest.raises(NotImplementedError, match=f"^Framework span_marker is not supported for this"):
            trainer = ArgillaTrainer(
                dataset=dataset,
                task=task,
                framework=framework,
                model=model,
                framework_kwargs={
                    "model_card_kwargs": {"license": "mit", "language": ["en", "es"], "dataset_name": DATASET_NAME}
                },
            )
        return
    else:
        trainer = ArgillaTrainer(
            dataset=dataset,
            task=task,
            framework=framework,
            model=model,
            framework_kwargs={
                "model_card_kwargs": {"license": "mit", "language": ["en", "es"], "dataset_name": DATASET_NAME}
            },
        )

    if framework in [Framework("spacy"), Framework("spacy-transformers")]:
        trainer.update_config(max_steps=1)
    elif framework in [Framework("transformers"), Framework("setfit")]:
        trainer.update_config(num_iterations=1)

    train_with_cleanup(trainer, OUTPUT_DIR)

    trainer.generate_model_card(OUTPUT_DIR)
    model_card_path = Path(OUTPUT_DIR) / "MODEL_CARD.md"
    assert (model_card_path).exists()

    try:
        assert (model_card_path).exists()
        content = model_card_path.read_text()
        if framework == Framework("transformers"):
            if task_type == "for_text_classification":
                pattern = patterns.TRANSFORMERS_CODE_SNIPPET
            else:
                pattern = patterns.TRANSFORMERS_QA_CODE_SNIPPET
        elif framework == Framework("setfit"):
            pattern = patterns.SETFIT_CODE_SNIPPET
        elif framework == Framework("peft"):
            pattern = patterns.PEFT_CODE_SNIPPET
        elif framework == Framework("spacy"):
            pattern = patterns.SPACY_CODE_SNIPPET
        elif framework == Framework("spacy-transformers"):
            pattern = patterns.SPACY_TRANSFORMERS_CODE_SNIPPET

        assert content.find(pattern) > -1

    finally:
        if Path(OUTPUT_DIR).exists():
            shutil.rmtree(OUTPUT_DIR)


@pytest.mark.usefixtures(
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_guidelines",
    "feedback_dataset_records",
)
def test_model_card_sentence_transformers(
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_guidelines: str,
    feedback_dataset_records: List["FeedbackRecord"],
) -> None:
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 2)

    def formatting_func(sample):
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
                return {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 1}
            elif labels[0] == "c":
                return [
                    {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 1},
                    {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 0},
                ]

    task = TrainingTask.for_sentence_similarity(formatting_func=formatting_func)

    trainer = ArgillaTrainer(
        dataset=dataset,
        task=task,
        framework="sentence-transformers",
        framework_kwargs={
            "cross_encoder": False,
            "model_card_kwargs": {"license": "mit", "language": ["en", "es"], "dataset_name": DATASET_NAME},
        },
    )
    trainer.update_config(epochs=1, batch_size=3)

    train_with_cleanup(trainer, OUTPUT_DIR)

    trainer.generate_model_card(OUTPUT_DIR)

    model_card_path = Path(OUTPUT_DIR) / "MODEL_CARD.md"

    try:
        assert (model_card_path).exists()
        content = model_card_path.read_text()
        assert content.find(patterns.SENTENCE_TRANSFORMERS_CODE_SNIPPET) > -1

    finally:
        if Path(OUTPUT_DIR).exists():
            shutil.rmtree(OUTPUT_DIR)


def test_model_card_openai(mocked_openai):
    dataset = FeedbackDataset.from_huggingface("argilla/customer_assistant")
    # adapation from LlamaIndex's TEXT_QA_PROMPT_TMPL_MSGS[1].content
    user_message_prompt = """Context information is below.
    ---------------------
    {context_str}
    ---------------------
    Given the context information and not prior knowledge but keeping your Argilla Cloud assistant style, answer the query.
    Query: {query_str}
    Answer:
    """
    # adapation from LlamaIndex's TEXT_QA_SYSTEM_PROMPT
    system_prompt = """You are an expert customer service assistant for the Argilla Cloud product that is trusted around the world."""

    def formatting_func(sample: dict):
        from uuid import uuid4

        if sample["response"]:
            chat = str(uuid4())
            user_message = user_message_prompt.format(context_str=sample["context"], query_str=sample["user-message"])
            return [
                (chat, "0", "system", system_prompt),
                (chat, "1", "user", user_message),
                (chat, "2", "assistant", sample["response"][0]["value"]),
            ]
        else:
            return None

    task = TrainingTask.for_chat_completion(formatting_func=formatting_func)
    trainer = ArgillaTrainer(
        dataset=dataset,
        task=task,
        framework="openai",
    )

    train_with_cleanup(trainer, OUTPUT_DIR)

    trainer.generate_model_card(OUTPUT_DIR)
    model_card_path = Path(OUTPUT_DIR) / "MODEL_CARD.md"

    try:
        assert (model_card_path).exists()
        content = model_card_path.read_text()

        assert content.find(patterns.OPENAI_CODE_SNIPPET) > -1

    finally:
        pass
        # if Path(OUTPUT_DIR).exists():
        #     shutil.rmtree(OUTPUT_DIR)


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


def formatting_func_ppo(sample: Dict[str, Any]):
    return sample["text"]


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
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_guidelines",
    "feedback_dataset_records",
)
def test_model_card_trl(
    formatting_func: Callable,
    training_task: Callable,
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
    task = training_task(formatting_func)

    model_id = "sshleifer/tiny-gpt2"
    trainer = ArgillaTrainer(
        dataset=dataset,
        task=task,
        framework="trl",
        model=model_id,
        framework_kwargs={
            "model_card_kwargs": {"license": "mit", "language": ["en", "es"], "dataset_name": DATASET_NAME}
        },
    )
    if training_task == TrainingTask.for_proximal_policy_optimization:
        from transformers import pipeline
        from trl import PPOConfig

        reward_model = pipeline("sentiment-analysis", model="lvwerra/distilbert-imdb")
        trainer.update_config(config=PPOConfig(batch_size=1, ppo_epochs=2), reward_model=reward_model)
    else:
        trainer.update_config(max_steps=1)

    train_with_cleanup(trainer, OUTPUT_DIR)

    trainer.generate_model_card(OUTPUT_DIR)
    model_card_path = Path(OUTPUT_DIR) / "MODEL_CARD.md"

    try:
        assert (model_card_path).exists()
        content = model_card_path.read_text()

        if training_task == TrainingTask.for_supervised_fine_tuning:
            pattern = patterns.TR_SFT_CODE_SNIPPET
        elif training_task == TrainingTask.for_reward_modeling:
            pattern = patterns.TR_RM_CODE_SNIPPET
        elif training_task == TrainingTask.for_proximal_policy_optimization:
            pattern = patterns.TR_PPO_CODE_SNIPPET
        elif training_task == TrainingTask.for_direct_preference_optimization:
            pattern = patterns.TR_DPO_CODE_SNIPPET

        assert content.find(pattern) > -1

    finally:
        if Path(OUTPUT_DIR).exists():
            shutil.rmtree(OUTPUT_DIR)


default_transformer_args = get_default_args(TrainingArguments.__init__)
default_transformer_args_1 = default_transformer_args.copy()
default_transformer_args_1.update({"output_dir": None, "warmup_steps": 100})
default_transformer_args_2 = default_transformer_args.copy()
default_transformer_args_2.update({"output_dir": {"nested_name": "test"}})
default_transformer_args_3 = default_transformer_args.copy()
default_transformer_args_3.update({"output_dir": [1.2, 3, "value"]})

# Test a random class, it could be a loss function passed as a callable, or an instance
# of one for example.
from dataclasses import dataclass


@dataclass
class Dummy:
    pass


default_transformer_args_4 = default_transformer_args.copy()
default_transformer_args_4.update({"output_dir": Dummy, "other": Dummy()})


# TODO(plaguss): Move these tests to test/unit
@pytest.mark.parametrize(
    "current_kwargs, new_kwargs",
    (
        (default_transformer_args_1, {"warmup_steps": 100}),
        (default_transformer_args_2, {"output_dir": {"nested_name": "test"}}),
        (default_transformer_args_3, {"output_dir": [1.2, 3, "value"]}),
        (default_transformer_args_4, {"output_dir": Dummy, "other": Dummy()}),
    ),
)
def test_updated_kwargs(current_kwargs: Dict[str, Any], new_kwargs: Dict[str, Any]):
    # Using only the Transformer's TrainingArguments as an example, no need to check if the arguments are correct

    new_arguments = _updated_arguments(default_transformer_args, current_kwargs)
    assert set(_prepare_dict_for_comparison(new_arguments).items()) == set(
        _prepare_dict_for_comparison(new_kwargs).items()
    )
