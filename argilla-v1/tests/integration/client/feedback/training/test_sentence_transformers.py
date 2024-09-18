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

from typing import TYPE_CHECKING, Callable, List, Union

import pytest
from argilla_v1.client.feedback.dataset import FeedbackDataset
from argilla_v1.client.feedback.schemas.fields import TextField
from argilla_v1.client.feedback.schemas.questions import LabelQuestion
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.feedback.training.base import ArgillaTrainer
from argilla_v1.client.feedback.training.schemas.base import (
    LabelQuestion,
    RatingQuestionUnification,
    TrainingTask,
)
from sentence_transformers import CrossEncoder, InputExample, SentenceTransformer

from tests.integration.client.feedback.helpers import (
    formatting_func_sentence_transformers,
    formatting_func_sentence_transformers_all_lists,
    formatting_func_sentence_transformers_case_1_b,
    formatting_func_sentence_transformers_case_2,
    formatting_func_sentence_transformers_case_3_a,
    formatting_func_sentence_transformers_case_3_b,
    formatting_func_sentence_transformers_case_4,
    formatting_func_sentence_transformers_rating_question,
)
from tests.integration.training.helpers import train_with_cleanup

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes

__OUTPUT_DIR__ = "tmp"
__FRAMEWORK__ = "sentence-transformers"


def formatting_func_errored(sample):
    labels = [
        annotation["value"]
        for annotation in sample["question-3"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    if labels:
        return sample["text"], sample["text"], sample["text"]


@pytest.mark.parametrize("cross_encoder,model_type", [(False, SentenceTransformer), (True, CrossEncoder)])
@pytest.mark.parametrize(
    "formatting_func",
    [
        formatting_func_sentence_transformers,
        formatting_func_sentence_transformers_all_lists,
        formatting_func_sentence_transformers_case_1_b,
        formatting_func_sentence_transformers_case_2,
        formatting_func_sentence_transformers_case_3_b,
        formatting_func_sentence_transformers_case_4,
        formatting_func_sentence_transformers_rating_question,
    ],
)
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_prepare_for_training_sentence_transformers(
    cross_encoder: bool,
    model_type: Union[SentenceTransformer, CrossEncoder],
    formatting_func: Callable,
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

    if formatting_func.__name__ == "formatting_func_sentence_transformers_rating_question":
        label_strategy = RatingQuestionUnification(question=dataset.question_by_name("question-2"), strategy="majority")
        task = TrainingTask.for_sentence_similarity(formatting_func=formatting_func, label_strategy=label_strategy)
    else:
        task = TrainingTask.for_sentence_similarity(formatting_func=formatting_func)

    train_dataset = dataset.prepare_for_training(framework=__FRAMEWORK__, task=task)

    assert isinstance(train_dataset, list)
    assert isinstance(train_dataset[0], InputExample)

    train_dataset, test_dataset = dataset.prepare_for_training(framework=__FRAMEWORK__, task=task, train_size=0.5)

    if cross_encoder:
        if ("case_3_b" in formatting_func.__name__) or ("case_4" in formatting_func.__name__):
            with pytest.raises(ValueError, match=r"^Cross-encoders don't support training with triplets"):
                trainer = ArgillaTrainer(
                    dataset=dataset,
                    task=task,
                    framework="sentence-transformers",
                    framework_kwargs={"cross_encoder": cross_encoder},
                )
            return

    trainer = ArgillaTrainer(
        dataset=dataset, task=task, framework=__FRAMEWORK__, framework_kwargs={"cross_encoder": cross_encoder}
    )
    trainer.update_config(batch_size=2)
    assert trainer._trainer.data_kwargs["batch_size"] == 2
    trainer.update_config(epochs=1)
    assert trainer._trainer.trainer_kwargs["epochs"] == 1
    train_with_cleanup(trainer, __OUTPUT_DIR__)
    # Check we have a bi-encoder/cross-encoder
    assert isinstance(trainer.get_trainer(), model_type)

    eval_trainer = ArgillaTrainer(
        dataset=dataset,
        task=task,
        framework=__FRAMEWORK__,
        train_size=0.5,
        framework_kwargs={"cross_encoder": cross_encoder},
    )
    eval_trainer.update_config(epochs=1)
    train_with_cleanup(eval_trainer, __OUTPUT_DIR__)

    assert len(eval_trainer.predict([["first sentence", "second sentence"], ["to compare", "another one"]])) == 2
    assert len(eval_trainer.predict(["first sentence", ["to compare", "another one"]])) == 2


def test_task_with_different_naming():
    dataset = FeedbackDataset(
        fields=[
            TextField(name="query"),
            TextField(name="retrieved_document_1"),
        ],
        questions=[
            LabelQuestion(
                name="sentence_similarity",
                labels={"0": "Not-similar", "1": "Missing-information", "2": "Similar"},
            ),
        ],
    )

    records = [
        FeedbackRecord(
            fields={"query": "some text", "retrieved_document_1": "retrieved data"},
            responses=[{"values": {"sentence_similarity": {"value": value}}}],
        )
        for value in ["0", "1", "2"]
    ]

    dataset.add_records(records)

    task = TrainingTask.for_sentence_similarity(
        texts=[dataset.field_by_name("query"), dataset.field_by_name("retrieved_document_1")],
        label=dataset.question_by_name("sentence_similarity"),
    )
    train_dataset = dataset.prepare_for_training(framework=__FRAMEWORK__, task=task)
    assert all(example.label == label for example, label in zip(train_dataset, [0, 1, 2]))


@pytest.mark.parametrize("cross_encoder", [False, True])
@pytest.mark.parametrize("formatting_func", [formatting_func_sentence_transformers_case_3_a, formatting_func_errored])
@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_prepare_for_training_sentence_transformers_bad_format(
    cross_encoder: bool,
    formatting_func: Callable,
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
    dataset.add_records(records=feedback_dataset_records)

    task = TrainingTask.for_sentence_similarity(formatting_func=formatting_func)

    # Match the start of the error message only
    if "errored" in formatting_func.__name__:
        match_start = r"^formatting_func must return"
    else:
        match_start = r"^Datasets containing a `sentence`"

    with pytest.raises(ValueError, match=match_start):
        ArgillaTrainer(
            dataset=dataset,
            task=task,
            framework="sentence-transformers",
            framework_kwargs={"cross_encoder": cross_encoder},
        )


@pytest.mark.parametrize("use_label", [False, True])
@pytest.mark.parametrize("cross_encoder", [False, True])
def test_prepare_for_training_sentence_transformers_with_defaults(
    use_label: bool,
    cross_encoder: bool,
) -> None:
    dataset = FeedbackDataset.from_huggingface("plaguss/snli-small", split="train[:8]")

    if use_label:
        task = TrainingTask.for_sentence_similarity(
            texts=[dataset.field_by_name("premise"), dataset.field_by_name("hypothesis")],
            label=dataset.question_by_name("label"),
        )
    else:
        task = TrainingTask.for_sentence_similarity(
            texts=[dataset.field_by_name("premise"), dataset.field_by_name("hypothesis")]
        )

    trainer = ArgillaTrainer(
        dataset=dataset, task=task, framework=__FRAMEWORK__, framework_kwargs={"cross_encoder": cross_encoder}
    )
    trainer.update_config(batch_size=2)
    assert trainer._trainer.data_kwargs["batch_size"] == 2
    trainer.update_config(epochs=1)
    assert trainer._trainer.trainer_kwargs["epochs"] == 1
    train_with_cleanup(trainer, __OUTPUT_DIR__)

    eval_trainer = ArgillaTrainer(
        dataset=dataset,
        task=task,
        framework=__FRAMEWORK__,
        train_size=0.5,
        framework_kwargs={"cross_encoder": cross_encoder},
    )
    eval_trainer.update_config(epochs=1)
    train_with_cleanup(eval_trainer, __OUTPUT_DIR__)

    assert len(eval_trainer.predict([["first sentence", "second sentence"], ["to compare", "another one"]])) == 2
    assert len(eval_trainer.predict(["first sentence", ["to compare", "another one"]])) == 2


@pytest.mark.usefixtures(
    "feedback_dataset_guidelines",
    "feedback_dataset_fields",
    "feedback_dataset_questions",
    "feedback_dataset_records",
)
def test_push_to_huggingface(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_records: List[FeedbackRecord],
    mocked_trainer_push_to_huggingface,
) -> None:
    # This framework is not implemented yet. Cross-Encoder models don't implement the functionality
    # for pushing a model to huggingface, and SentenceTransformer models have the functionality
    # but is outdated and doesn't work with the current versions of 'huggingface-hub'.
    # The present test is let here for the future, when we either implement the functionality
    # in 'argilla', or to 'sentence-transformers'.

    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
    )
    dataset.add_records(records=feedback_dataset_records * 2)

    task = TrainingTask.for_sentence_similarity(formatting_func=formatting_func_sentence_transformers)

    model = "all-MiniLM-L6-v2"

    trainer = ArgillaTrainer(dataset=dataset, task=task, framework=__FRAMEWORK__, model=model)

    trainer.update_config(max_steps=1)

    train_with_cleanup(trainer, __OUTPUT_DIR__)
    with pytest.raises(
        NotImplementedError, match="This method is not implemented for `ArgillaSentenceTransformersTrainer`."
    ):
        trainer.push_to_huggingface("mocked", generate_card=True)
