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

import random
from collections import Counter
from typing import TYPE_CHECKING, Callable, List, Union

import pytest

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes

import re
import shutil
import sys
from pathlib import Path

from argilla_v1.client.feedback.dataset import FeedbackDataset
from argilla_v1.client.feedback.schemas import (
    FeedbackRecord,
    LabelQuestion,
    MultiLabelQuestion,
)
from argilla_v1.client.feedback.schemas.enums import ResponseStatusFilter
from argilla_v1.client.feedback.schemas.records import SortBy
from argilla_v1.client.feedback.training import ArgillaTrainer
from argilla_v1.client.feedback.training.schemas.base import (
    TrainingTask,
    TrainingTaskForTextClassification,
    TrainingTaskMapping,
    TrainingTaskMappingForTextClassification,
    TrainingTaskTypes,
)
from argilla_v1.client.feedback.training.schemas.return_types import (
    QuestionAnsweringReturnTypes,
    TextClassificationReturnTypes,
)
from argilla_v1.client.feedback.unification import LabelQuestionUnification
from argilla_v1.client.models import Framework
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from tests.integration.training.helpers import train_with_cleanup

__OUTPUT_DIR__ = "tmp"


@pytest.mark.parametrize(
    "framework",
    [
        Framework("spacy"),
        Framework("spacy-transformers"),
        Framework("transformers"),
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
            train_with_cleanup(trainer, __OUTPUT_DIR__)

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
        train_with_cleanup(trainer, __OUTPUT_DIR__)

        # Assert that the provided tokenizer is used
        assert (
            trainer._trainer.trainer_tokenizer.pretrained_init_configuration == tokenizer.pretrained_init_configuration
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
            f"formatting_func must return {TextClassificationReturnTypes.__annotations__['format']}, not <class 'list'>"
        ),
    ):
        task = TrainingTask.for_text_classification(wrong_formatting_func)
        trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework)
        trainer.update_config(num_iterations=1)
        train_with_cleanup(trainer, __OUTPUT_DIR__)

    def correct_formatting_func(sample):
        data = wrong_formatting_func(sample)
        if data:
            yield (data["text"], data["label"])
        else:
            yield None

    task = TrainingTask.for_text_classification(correct_formatting_func)
    trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework)
    trainer.update_config(num_iterations=1)
    train_with_cleanup(trainer, __OUTPUT_DIR__)

    def correct_formatting_func_with_yield(sample):
        data = wrong_formatting_func(sample)
        if data:
            yield (data["text"], data["label"])
        else:
            yield None

    task = TrainingTask.for_text_classification(correct_formatting_func_with_yield)
    trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework)
    trainer.update_config(num_iterations=1)
    train_with_cleanup(trainer, __OUTPUT_DIR__)


def formatting_func_std(sample):
    responses = []
    question = sample["label"]
    context = sample["text"]
    for answer in sample["question-1"]:
        if not all([question, context, answer["value"]]):
            continue
        responses.append((question, context, answer["value"]))
    return responses


def formatting_func_with_yield(sample):
    question = sample["label"]
    context = sample["text"]
    for answer in sample["question-1"]:
        if not all([question, context, answer["value"]]):
            continue
        yield question, context, answer["value"]


@pytest.mark.skip(
    reason="For some reason this test fails in CI, but not locally. It just says: Error: The operation was canceled."
)
@pytest.mark.parametrize(
    "formatting_func",
    (formatting_func_std, formatting_func_with_yield),
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_question_answering_with_formatting_func(
    feedback_dataset_fields,
    feedback_dataset_questions,
    feedback_dataset_records,
    feedback_dataset_guidelines,
    formatting_func,
):
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 2)
    with pytest.raises(
        ValueError,
        match=re.escape(
            f"formatting_func must return {QuestionAnsweringReturnTypes.__annotations__['format']}, not <class 'list'>"
        ),
    ):
        task = TrainingTask.for_question_answering(lambda x: {})
        ArgillaTrainer(dataset=dataset, task=task, framework="transformers")

    task = TrainingTask.for_question_answering(formatting_func)
    trainer = ArgillaTrainer(dataset=dataset, task=task, framework="transformers")
    trainer.update_config(num_iterations=1)
    train_with_cleanup(trainer, __OUTPUT_DIR__)


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
    trainer = ArgillaTrainer(dataset=dataset, task=task, framework="transformers", train_size=0.8)
    trainer.update_config(num_iterations=1)
    train_with_cleanup(trainer, __OUTPUT_DIR__)


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


@pytest.mark.parametrize(
    "framework",
    [
        Framework("spacy"),
        Framework("spacy-transformers"),
        Framework("transformers"),
        Framework("setfit"),
        Framework("peft"),
        # The FeedbackDataset needs to work with token classification for this framework to work.
        Framework("span_marker"),
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
    mocked_trainer_push_to_huggingface,
) -> None:
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
            ArgillaTrainer(dataset=dataset, task=task, framework=framework)
        return

    else:
        if framework == Framework("spacy"):
            model = "en_core_web_sm"
        elif framework == Framework("setfit"):
            model = "all-MiniLM-L6-v2"
        else:
            model = "prajjwal1/bert-tiny"

        trainer = ArgillaTrainer(dataset=dataset, task=task, framework=framework, model=model)

    # We need to initialize the model (is faster than calling the whole training process) before calling push_to_huggingface.
    # The remaining models need to call the train method first.
    repo_id = "mocked"
    if framework in (Framework("transformers"), Framework("peft")):
        trainer.update_config(num_iterations=1)
        trainer._trainer.init_model(new=True)
    elif framework in (Framework("setfit"), Framework("spacy"), Framework("spacy-transformers")):
        if framework in (Framework("spacy"), Framework("spacy-transformers")):
            trainer.update_config(max_steps=1)
            repo_id = __OUTPUT_DIR__
        else:
            trainer.update_config(num_iterations=1)
    else:
        trainer._trainer.init_model()

    # We have to train the model and push it with spacy before removing the
    # generated folder, as it needs to be packaged.
    if framework in (Framework("spacy"), Framework("spacy-transformers")):
        trainer.train(__OUTPUT_DIR__)
    else:
        trainer.train(__OUTPUT_DIR__)

    # This functionality is mocked, no need to check the generated card too.
    trainer.push_to_huggingface(repo_id, generate_card=False)
    if Path(__OUTPUT_DIR__).exists():
        shutil.rmtree(__OUTPUT_DIR__)


@pytest.mark.parametrize(
    "statuses, sort_by, sorted_results, max_records",
    [
        ([], None, [2, 4, 4, 5, 6, 2, 4, 4, 5, 6], None),
        ([], [SortBy(field="metadata.integer-metadata", order="desc")], [6, 6, 5, 5, 4, 4, 4, 4, 2, 2], 4),
        ([ResponseStatusFilter.submitted], None, [2, 4, 5, 6], None),
        (
            [ResponseStatusFilter.discarded, ResponseStatusFilter.submitted],
            [SortBy(field="metadata.integer-metadata", order="asc")],
            [2, 2, 4, 4, 5, 5, 6, 6],
            None,
        ),
    ],
)
def test_trainer_with_filter_by_and_sort_by_and_max_records(
    test_remote_dataset_with_records: "FeedbackDataset",
    statuses: List[ResponseStatusFilter],
    sort_by: SortBy,
    sorted_results: List[int],
    max_records: int,
) -> None:
    questions = [
        question
        for question in test_remote_dataset_with_records.questions
        if isinstance(question, (LabelQuestion, MultiLabelQuestion))
    ]
    task = TrainingTask.for_text_classification(text=test_remote_dataset_with_records.fields[0], label=questions[0])
    filter_by = None if len(statuses) == 0 else {"response_status": statuses}

    assert len(test_remote_dataset_with_records) == 10  # Number of records before filtering/sorting
    trainer = ArgillaTrainer(
        dataset=test_remote_dataset_with_records,
        task=task,
        framework="transformers",
        model="prajjwal1/bert-tiny",
        filter_by=filter_by,
        sort_by=sort_by,
        max_records=max_records,
    )
    if max_records is None:
        max_records = 99999
    metadatas = [r.metadata["integer-metadata"] for r in trainer._dataset.pull().records]
    assert len(trainer._dataset) == min(len(sorted_results), max_records)
    assert all([r == m for r, m in zip(sorted_results, metadatas)])
