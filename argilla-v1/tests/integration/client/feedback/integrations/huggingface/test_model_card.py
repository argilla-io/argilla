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

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Callable, List, Union

import pytest
from argilla_v1.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
)
from argilla_v1.client.feedback.unification import LabelQuestionUnification
from argilla_v1.client.models import Framework
from argilla_v1.feedback import ArgillaTrainer, FeedbackDataset, TrainingTask

from tests.integration.client.feedback.helpers import (
    formatting_func_chat_completion,
    formatting_func_dpo,
    formatting_func_ppo,
    formatting_func_rm,
    formatting_func_sentence_transformers,
    formatting_func_sft,
    model_card_pattern,
)

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas import FeedbackRecord
    from argilla_v1.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes


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
)
def test_model_card_with_defaults(
    framework: Union[Framework, str],
    training_task: str,
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
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
        with pytest.raises(NotImplementedError, match="^Framework span_marker is not supported for this"):
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
)
def test_model_card_sentence_transformers(
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_guidelines: str,
    feedback_dataset_records: List["FeedbackRecord"],
    mocked_is_on_huggingface,
) -> None:
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 2)

    task = TrainingTask.for_sentence_similarity(formatting_func=formatting_func_sentence_transformers)

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


def test_model_card_openai(mocked_openai, mocked_is_on_huggingface):
    dataset = FeedbackDataset.from_huggingface("argilla/customer_assistant")
    dataset._records = dataset._records[:3]
    task = TrainingTask.for_chat_completion(formatting_func=formatting_func_chat_completion)

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
        trainer.update_config(config=PPOConfig(batch_size=128, ppo_epochs=2), reward_model=reward_model)
    else:
        trainer.update_config(max_steps=1)

    with TemporaryDirectory() as tmpdirname:
        model_card = trainer.generate_model_card(tmpdirname)
        assert (Path(tmpdirname) / MODEL_CARD_NAME).exists()

        pattern = model_card_pattern(Framework("trl"), training_task)
        assert model_card.content.find(pattern) > -1
