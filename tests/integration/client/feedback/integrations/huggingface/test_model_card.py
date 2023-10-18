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
- spacy, spacy-transformers, transformers (text-classification and QA), setfit, and peft with
default dataset fields.
- sentence-transformers and trl with formatting_func.
"""

import shutil
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, List, Union

import pytest
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
)
from argilla.client.feedback.unification import LabelQuestionUnification
from argilla.client.models import Framework
from argilla.feedback import ArgillaTrainer, FeedbackDataset, TrainingTask

if TYPE_CHECKING:
    from argilla.client.feedback.schemas import FeedbackRecord
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes


DATASET_NAME = "argilla/emotion"
MODEL_CARD_NAME = "README.md"


@pytest.mark.parametrize(
    "framework, training_task",
    [
        (Framework("spacy"), TrainingTask.for_text_classification),
        (Framework("spacy-transformers"), TrainingTask.for_text_classification),
        (Framework("transformers"), TrainingTask.for_text_classification),
        (Framework("transformers"), TrainingTask.for_question_answering),
        (Framework("setfit"), TrainingTask.for_text_classification),
        (Framework("peft"), TrainingTask.for_text_classification),
        (Framework("span_marker"), TrainingTask.for_text_classification),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
    "model_card_pattern",
)
def test_model_card_with_defaults(
    framework: Union[Framework, str],
    training_task: str,
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
    model_card_pattern: str,
    mocked_is_on_huggingface,
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

    if training_task == TrainingTask.for_question_answering:
        task = TrainingTask.for_question_answering(
            question=dataset.field_by_name("label"),
            context=dataset.field_by_name("text"),
            answer=dataset.question_by_name("question-1"),
        )
        output_dir = '"question_answering_model"'
    elif training_task == TrainingTask.for_text_classification:
        task = TrainingTask.for_text_classification(text=dataset.fields[0], label=label)
        output_dir = '"text_classification_model"'

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
                "model_card_kwargs": {
                    "license": "mit",
                    "language": ["en", "es"],
                    "dataset_name": DATASET_NAME,
                    "output_dir": output_dir,
                },
            },
        )

    if framework in [Framework("spacy"), Framework("spacy-transformers")]:
        trainer.update_config(max_steps=1)
    elif framework in [Framework("transformers"), Framework("setfit")]:
        trainer.update_config(num_iterations=1)

    with TemporaryDirectory() as tmpdirname:
        model_card = trainer.generate_model_card(tmpdirname)
        assert (Path(tmpdirname) / MODEL_CARD_NAME).exists()
        pattern = model_card_pattern(framework, training_task)
        assert model_card.content.find(pattern) > -1


@pytest.mark.usefixtures(
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_guidelines",
    "feedback_dataset_records",
    "model_card_pattern",
)
def test_model_card_sentence_transformers(
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_guidelines: str,
    feedback_dataset_records: List["FeedbackRecord"],
    model_card_pattern: str,
    mocked_is_on_huggingface,
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
            "model_card_kwargs": {
                "license": "mit",
                "language": ["en", "es"],
                "dataset_name": DATASET_NAME,
                "output_dir": '"sentence_similarity_model"',
            },
        },
    )
    trainer.update_config(epochs=1, batch_size=3)

    with TemporaryDirectory() as tmpdirname:
        model_card = trainer.generate_model_card(tmpdirname)
        assert (Path(tmpdirname) / MODEL_CARD_NAME).exists()
        pattern = model_card_pattern(Framework("sentence-transformers"), TrainingTask.for_sentence_similarity)
        assert model_card.content.find(pattern) > -1


@pytest.mark.usefixtures(
    "model_card_pattern",
)
def test_model_card_openai(model_card_pattern: str, mocked_openai, mocked_is_on_huggingface):
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

    trainer = ArgillaTrainer(
        dataset=dataset,
        task=task,
        framework="openai",
        model="gpt-3.5-turbo-0613",
        framework_kwargs={
            "model_card_kwargs": {
                "license": "mit",
                "language": ["en", "es"],
                "dataset_name": DATASET_NAME,
                "output_dir": '"chat_completion_model"',
            }
        },
    )

    with TemporaryDirectory() as tmpdirname:
        model_card = trainer.generate_model_card(tmpdirname)
        assert (Path(tmpdirname) / MODEL_CARD_NAME).exists()
        pattern = model_card_pattern(Framework("openai"), TrainingTask.for_chat_completion)
        assert model_card.content.find(pattern) > -1


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
    "model_card_pattern",
)
def test_model_card_trl(
    formatting_func: Callable,
    training_task: Callable,
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
    model_card_pattern: str,
    mocked_is_on_huggingface,
) -> None:
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 2)
    task = training_task(formatting_func)
    model_id = "sshleifer/tiny-gpt2"

    if training_task == TrainingTask.for_supervised_fine_tuning:
        output_dir = '"sft_model"'
    elif training_task == TrainingTask.for_reward_modeling:
        output_dir = '"rm_model"'
    elif training_task == TrainingTask.for_proximal_policy_optimization:
        output_dir = '"ppo_model"'
    else:
        output_dir = '"dpo_model"'

    trainer = ArgillaTrainer(
        dataset=dataset,
        task=task,
        framework="trl",
        model=model_id,
        framework_kwargs={
            "model_card_kwargs": {
                "license": "mit",
                "language": ["en", "es"],
                "dataset_name": DATASET_NAME,
                "output_dir": output_dir,
            }
        },
    )
    if training_task == TrainingTask.for_proximal_policy_optimization:
        from transformers import pipeline
        from trl import PPOConfig

        reward_model = pipeline("sentiment-analysis", model="lvwerra/distilbert-imdb")
        trainer.update_config(config=PPOConfig(batch_size=1, ppo_epochs=2), reward_model=reward_model)
    else:
        trainer.update_config(max_steps=1)

    with TemporaryDirectory() as tmpdirname:
        model_card = trainer.generate_model_card(tmpdirname)
        assert (Path(tmpdirname) / MODEL_CARD_NAME).exists()
        pattern = model_card_pattern(Framework("trl"), training_task)
        assert model_card.content.find(pattern) > -1
