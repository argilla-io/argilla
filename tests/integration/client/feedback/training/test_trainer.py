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

import json
import random
from collections import Counter
from typing import TYPE_CHECKING, Callable, List, Union

import pytest

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes

import re
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
    TrainingTaskForQuestionAnsweringFormat,
    TrainingTaskForTextClassification,
    TrainingTaskForTextClassificationFormat,
    TrainingTaskMapping,
    TrainingTaskMappingForTextClassification,
    TrainingTaskTypes,
)
from argilla.client.feedback.unification import LabelQuestionUnification
from argilla.client.models import Framework
from huggingface_hub import HfApi, HfFolder, hf_hub_download
from transformers import AutoModelForSequenceClassification, AutoTokenizer

__OUTPUT_DIR__ = "tmp"

# To mimick the tests from huggingface_hub: https://github.com/huggingface/huggingface_hub/blob/v0.18.0.rc0/tests/testing_constants.py
HF_HUB_CONSTANTS = {
    "HF_HUB_ENDPOINT_STAGING": "https://hub-ci.huggingface.co",
    "HF_HUB_TOKEN": "hf_94wBhPGp6KrrTH3KDchhKpRxZwd6dmHWLL",
}


@pytest.mark.parametrize(
    "framework",
    [
        Framework("spacy"),
        Framework("spacy-transformers"),
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
def test_prepare_for_training_text_classification_with_defaults(
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
            trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework)
    elif framework == Framework("spark-nlp"):
        with pytest.raises(NotImplementedError, match=f"{framework} is not a valid framework."):
            trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework)
    else:
        if framework in [Framework("peft")] and sys.version_info < (3, 9):
            pass
        else:
            trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework)
            if framework in [Framework("spacy"), Framework("spacy-transformers")]:
                trainer.update_config(max_steps=1)
            elif framework in [Framework("transformers"), Framework("setfit")]:
                trainer.update_config(num_iterations=1)
            trainer.train(__OUTPUT_DIR__)

    if Path(__OUTPUT_DIR__).exists():
        shutil.rmtree(__OUTPUT_DIR__)


@pytest.mark.parametrize(
    "framework, model_id, target_modules",
    [
        (Framework("transformers"), "distilbert-base-cased", None),
        (Framework("peft"), "distilbert-base-cased", ["q_lin", "k_lin"]),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_argilla_trainer_text_classification_with_model_tokenizer(
    framework: Union[Framework, str],
    model_id: str,
    target_modules: Union[List[str], None],
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

    model = AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=3)
    tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="right", add_prefix_space=True)
    if not (framework == Framework("peft") and sys.version_info < (3, 9)):
        trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework, model=model, tokenizer=tokenizer)
        trainer.update_config(num_steps=1, target_modules=target_modules)
        trainer.train(__OUTPUT_DIR__)

        # Assert that the provided tokenizer is used
        assert (
            trainer._trainer._transformers_tokenizer.pretrained_init_configuration
            == tokenizer.pretrained_init_configuration
        )

    if Path(__OUTPUT_DIR__).exists():
        shutil.rmtree(__OUTPUT_DIR__)


@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_prepare_for_training_text_classification_with_formatting_func(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 5)
    framework = Framework("setfit")

    def wrong_formatting_func(sample):
        text = sample["text"]
        values = [resp["value"] for resp in sample["question-3"]]
        counter = Counter(values)
        if counter:
            most_common = counter.most_common()
            max_frequency = most_common[0][1]
            most_common_elements = [element for element, frequency in most_common if frequency == max_frequency]
            label = random.choice(most_common_elements)
            return {"text": text, "label": label}
        else:
            return None

    with pytest.raises(
        ValueError,
        match=re.escape(
            f"formatting_func must return {TrainingTaskForTextClassificationFormat.__annotations__['format']}, not <class 'dict'>"
        ),
    ):
        task = TrainingTask.for_text_classification(wrong_formatting_func)
        trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework)
        trainer.update_config(num_iterations=1)
        trainer.train(__OUTPUT_DIR__)

    def correct_formatting_func(sample):
        data = wrong_formatting_func(sample)
        if data:
            yield (data["text"], data["label"])
        else:
            yield None

    task = TrainingTask.for_text_classification(correct_formatting_func)
    trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework)
    trainer.update_config(num_iterations=1)
    trainer.train(__OUTPUT_DIR__)

    def correct_formatting_func_with_yield(sample):
        data = wrong_formatting_func(sample)
        if data:
            yield (data["text"], data["label"])
        else:
            yield None

    task = TrainingTask.for_text_classification(correct_formatting_func_with_yield)
    trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework)
    trainer.update_config(num_iterations=1)
    trainer.train(__OUTPUT_DIR__)


@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_question_answering_with_formatting_func(
    feedback_dataset_fields, feedback_dataset_questions, feedback_dataset_records, feedback_dataset_guidelines
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 5)
    with pytest.raises(
        ValueError,
        match=re.escape(
            f"formatting_func must return {TrainingTaskForQuestionAnsweringFormat.__annotations__['format']}, not <class 'dict'>"
        ),
    ):
        task = TrainingTask.for_question_answering(lambda x: {})
        trainer = ArgillaTrainer(dataset=dataset, task=task, framework="transformers")
        trainer.update_config(num_iterations=1)
        trainer.train(__OUTPUT_DIR__)

    def formatting_func(sample):
        responses = []
        question = sample["label"]
        context = sample["text"]
        for answer in sample["question-1"]:
            if not all([question, context, answer["value"]]):
                continue
            responses.append((question, context, answer["value"]))
        return responses

    task = TrainingTask.for_question_answering(formatting_func)
    trainer = ArgillaTrainer(dataset=dataset, task=task, framework="transformers")
    trainer.update_config(num_iterations=1)
    trainer.train(__OUTPUT_DIR__)

    def formatting_func_with_yield(sample):
        question = sample["label"]
        context = sample["text"]
        for answer in sample["question-1"]:
            if not all([question, context, answer["value"]]):
                continue
            yield question, context, answer["value"]

    task = TrainingTask.for_question_answering(formatting_func_with_yield)
    trainer = ArgillaTrainer(dataset=dataset, task=task, framework="transformers")
    trainer.update_config(num_iterations=1)
    trainer.train(__OUTPUT_DIR__)


@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_question_answering_without_formatting_func(
    feedback_dataset_fields, feedback_dataset_questions, feedback_dataset_records, feedback_dataset_guidelines
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 5)

    task = TrainingTask.for_question_answering(
        question=dataset.field_by_name("label"),
        context=dataset.field_by_name("text"),
        answer=dataset.question_by_name("question-1"),
    )
    trainer = ArgillaTrainer(dataset=dataset, task=task, framework="transformers")
    trainer.update_config(num_iterations=1)
    trainer.train(__OUTPUT_DIR__)


@pytest.mark.parametrize(
    "callable",
    (
        lambda: TrainingTaskMapping.for_text_classification(None, None),
        lambda: TrainingTaskMapping.for_direct_preference_optimization(None),
        lambda: TrainingTaskMapping.for_reward_modeling(None),
        lambda: TrainingTaskMapping.for_supervised_fine_tuning(None),
    ),
)
def test_deprecations(callable: Callable[[], TrainingTaskTypes]) -> None:
    with pytest.warns(DeprecationWarning, match="`TrainingTaskMapping` has been renamed to `TrainingTask`"):
        # This'll crash because we're passing None, but we only test the warning
        try:
            callable()
        except Exception:
            pass


def test_deprecations_for_text_classification():
    with pytest.warns(
        DeprecationWarning,
        match="`TrainingTaskMappingForTextClassification` has been renamed to `TrainingTaskForTextClassification`",
    ):
        # This'll crash because we're passing None, but we only test the warning
        try:
            TrainingTaskMappingForTextClassification(None)
        except Exception:
            pass


def test_tokenizer_warning_wrong_framework(
    feedback_dataset_fields,
    feedback_dataset_questions,
    feedback_dataset_records,
    feedback_dataset_guidelines,
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

    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    with pytest.warns(UserWarning, match="Passing a tokenizer is not supported for the setfit framework."):
        ArgillaTrainer(dataset=dataset, task=task, framework="setfit", tokenizer=tokenizer)


@pytest.mark.slow
@pytest.mark.parametrize(
    "framework",
    [
        # Framework("spacy"),
        # Framework("spacy-transformers"),
        Framework("transformers"),
        # Framework("span_marker"),
        # Framework("setfit"),
        # Framework("peft"),
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_push_to_huggingface(
    framework: Union[Framework, str],
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
) -> None:
    # The token will be grabbed internally, but fail and warn soon if the user has no token available
    token = HfFolder.get_token()
    if token is None:
        raise ValueError("No token available, please set it with the following env var name: 'HUGGING_FACE_HUB_TOKEN'")

    hf_api = HfApi()

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
    task = TrainingTask.for_text_classification(text=dataset.fields[0], label=label)

    if framework == Framework("span_marker"):
        with pytest.raises(
            NotImplementedError,
            match=f"Framework {framework} is not supported for this {TrainingTaskForTextClassification}.",
        ):
            trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework)

    else:
        if framework == Framework("spacy"):
            model = "en_core_web_sm"
        elif framework == Framework("setfit"):
            model = "all-MiniLM-L6-v2"
        else:
            model = "prajjwal1/bert-tiny"

        trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework, model=model)

    # We need to initialize the model (is faster than calling the whole training process) before calling push_to_huggingface.
    if framework == Framework("transformers"):
        trainer._trainer.init_model(new=True)
    else:
        trainer._trainer.init_model()

    # NOTE: This is just to test locally, we need a better solution for the CI.
    repo_id = "plaguss/test_model"

    trainer.push_to_huggingface(repo_id, generate_card=True)

    # Check the repo is created.
    # For the moment, the same check done at: https://github.com/huggingface/huggingface_hub/blob/v0.18.0.rc0/tests/test_hubmixin.py#L154
    model_info = hf_api.model_info(repo_id)
    assert model_info.modelId == repo_id

    tmp_config_path = hf_hub_download(
        repo_id=repo_id,
        filename="config.json",
        use_auth_token=token,
    )

    with open(tmp_config_path) as f:
        conf = json.load(f)
        assert isinstance(conf, dict)
        assert len(conf) > 0

    # No need to test this file, if the download succeeds its working
    tmp_readme_path = hf_hub_download(
        repo_id=repo_id,
        filename="README.md",
        use_auth_token=token,
    )

    # Delete repo
    hf_api.delete_repo(repo_id=repo_id)
