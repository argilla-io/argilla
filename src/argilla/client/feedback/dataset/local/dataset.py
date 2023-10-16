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
import logging
import textwrap
import warnings
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Union

from argilla.client.feedback.constants import FETCHING_BATCH_SIZE
from argilla.client.feedback.dataset.base import FeedbackDatasetBase
from argilla.client.feedback.dataset.local.mixins import ArgillaMixin
from argilla.client.feedback.schemas.questions import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla.client.feedback.schemas.types import AllowedQuestionTypes
from argilla.client.feedback.training.schemas import (
    TrainingTaskForChatCompletion,
    TrainingTaskForDPO,
    TrainingTaskForPPO,
    TrainingTaskForQuestionAnswering,
    TrainingTaskForRM,
    TrainingTaskForSentenceSimilarity,
    TrainingTaskForSFT,
    TrainingTaskForTextClassification,
    TrainingTaskTypes,
)
from argilla.client.feedback.unification import (
    LabelQuestionStrategy,
    MultiLabelQuestionStrategy,
    RankingQuestionStrategy,
    RatingQuestionStrategy,
    TextQuestionStrategy,
)
from argilla.client.models import Framework
from argilla.utils.dependency import require_dependencies

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.records import FeedbackRecord
    from argilla.client.feedback.schemas.types import AllowedFieldTypes


_LOGGER = logging.getLogger(__name__)


class FeedbackDataset(ArgillaMixin, FeedbackDatasetBase):
    def __init__(
        self,
        *,
        fields: List["AllowedFieldTypes"],
        questions: List[AllowedQuestionTypes],
        guidelines: Optional[str] = None,
    ) -> None:
        """Initializes a `FeedbackDataset` instance locally.

        Args:
            fields: contains the fields that will define the schema of the records in the dataset.
            questions: contains the questions that will be used to annotate the dataset.
            guidelines: contains the guidelines for annotating the dataset. Defaults to `None`.

        Raises:
            TypeError: if `fields` is not a list of `FieldSchema`.
            ValueError: if `fields` does not contain at least one required field.
            TypeError: if `questions` is not a list of `TextQuestion`, `RatingQuestion`,
                `LabelQuestion`, and/or `MultiLabelQuestion`.
            ValueError: if `questions` does not contain at least one required question.
            TypeError: if `guidelines` is not None and not a string.
            ValueError: if `guidelines` is an empty string.

        Examples:
            >>> import argilla as rg
            >>> rg.init(api_url="...", api_key="...")
            >>> dataset = rg.FeedbackDataset(
            ...     fields=[
            ...         rg.TextField(name="text", required=True),
            ...         rg.TextField(name="label", required=True),
            ...     ],
            ...     questions=[
            ...         rg.TextQuestion(
            ...             name="question-1",
            ...             description="This is the first question",
            ...             required=True,
            ...         ),
            ...         rg.RatingQuestion(
            ...             name="question-2",
            ...             description="This is the second question",
            ...             required=True,
            ...             values=[1, 2, 3, 4, 5],
            ...         ),
            ...         rg.LabelQuestion(
            ...             name="question-3",
            ...             description="This is the third question",
            ...             required=True,
            ...             labels=["positive", "negative"],
            ...         ),
            ...         rg.MultiLabelQuestion(
            ...             name="question-4",
            ...             description="This is the fourth question",
            ...             required=True,
            ...             labels=["category-1", "category-2", "category-3"],
            ...         ),
            ...     ],
            ...     guidelines="These are the annotation guidelines.",
            ... )
        """
        super().__init__(fields=fields, questions=questions, guidelines=guidelines)

        self._records = []

    @property
    def records(self) -> List["FeedbackRecord"]:
        """Returns the records in the dataset."""
        return self._records

    def __repr__(self) -> str:
        """Returns a string representation of the dataset."""
        return (
            "FeedbackDataset("
            + textwrap.indent(
                f"\nfields={self.fields}\nquestions={self.questions}\nguidelines={self.guidelines})", "    "
            )
            + "\n)"
        )

    def __len__(self) -> int:
        """Returns the number of records in the dataset."""
        return len(self._records)

    def __getitem__(self, key: Union[slice, int]) -> Union["FeedbackRecord", List["FeedbackRecord"]]:
        """Returns the record(s) at the given index(es).

        Args:
            key: the index(es) of the record(s) to return. Can either be a single index or a slice.

        Returns:
            Either the record of the given index, or a list with the records at the given indexes.
        """
        if len(self._records) < 1:
            raise RuntimeError(
                "In order to get items from `FeedbackDataset` you need to add them first" " with `add_records`."
            )
        if isinstance(key, int) and len(self._records) < key:
            raise IndexError(f"This dataset contains {len(self)} records, so index {key} is out of range.")
        return self._records[key]

    def iter(self, batch_size: Optional[int] = FETCHING_BATCH_SIZE) -> Iterator[List["FeedbackRecord"]]:
        """Returns an iterator over the records in the dataset.

        Args:
            batch_size: the size of the batches to return. Defaults to 100.
        """
        for i in range(0, len(self._records), batch_size):
            yield self._records[i : i + batch_size]

    def add_records(
        self, records: Union["FeedbackRecord", Dict[str, Any], List[Union["FeedbackRecord", Dict[str, Any]]]]
    ) -> None:
        """Adds the given records to the dataset, and stores them locally. If you are
        planning to push those to Argilla, you will need to call `push_to_argilla` afterwards,
        to both create the dataset in Argilla and push the records to it. Then, from a
        `FeedbackDataset` pushed to Argilla, you'll just need to call `add_records` and
        those will be automatically uploaded to Argilla.

        Args:
            records: can be a single `FeedbackRecord`, a list of `FeedbackRecord`,
                a single dictionary, or a list of dictionaries. If a dictionary is provided,
                it will be converted to a `FeedbackRecord` internally.

        Raises:
            ValueError: if the given records are an empty list.
            ValueError: if the given records are neither: `FeedbackRecord`, list of `FeedbackRecord`,
                list of dictionaries as a record or dictionary as a record.
            ValueError: if the given records do not match the expected schema.
        """
        records = self._parse_records(records)
        self._validate_records(records)

        if len(self._records) > 0:
            self._records += records
        else:
            self._records = records

    def pull(self) -> "FeedbackDataset":
        warnings.warn(
            "`pull` method is not supported for local datasets and won't take any effect."
            "First, you need to push the dataset to Argilla with `FeedbackDataset.push_to_argilla()`."
            "After, use `FeedbackDataset.from_argilla(...).pull()`.",
            UserWarning,
        )
        return self

    def filter_by(self, *args, **kwargs) -> "FeedbackDataset":
        warnings.warn(
            "`filter_by` method is not supported for local datasets and won't take any effect. "
            "First, you need to push the dataset to Argilla with `FeedbackDataset.push_to_argilla()`."
            "After, use `FeedbackDataset.from_argilla(...).filter_by()`.",
            UserWarning,
        )
        return self

    def delete(self):
        warnings.warn(
            "`delete` method is not supported for local datasets and won't take any effect. "
            "First, you need to push the dataset to Argilla with `FeedbackDataset.push_to_argilla`."
            "After, use `FeedbackDataset.from_argilla(...).delete()`",
            UserWarning,
        )
        return self

    def unify_responses(
        self: "FeedbackDatasetBase",
        question: Union[str, LabelQuestion, MultiLabelQuestion, RatingQuestion],
        strategy: Union[
            str, LabelQuestionStrategy, MultiLabelQuestionStrategy, RatingQuestionStrategy, RankingQuestionStrategy
        ],
    ) -> "FeedbackDataset":
        """
        The `unify_responses` function takes a question and a strategy as input and applies the strategy
        to unify the responses for that question.

        Args:
            question The `question` parameter can be either a string representing the name of the
                question, or an instance of one of the question classes (`LabelQuestion`, `MultiLabelQuestion`,
                `RatingQuestion`, `RankingQuestion`).
            strategy The `strategy` parameter is used to specify the strategy to be used for unifying
                responses for a given question. It can be either a string or an instance of a strategy class.
        """
        if isinstance(question, str):
            question = self.question_by_name(question)

        if isinstance(strategy, str):
            if isinstance(question, LabelQuestion):
                strategy = LabelQuestionStrategy(strategy)
            elif isinstance(question, MultiLabelQuestion):
                strategy = MultiLabelQuestionStrategy(strategy)
            elif isinstance(question, RatingQuestion):
                strategy = RatingQuestionStrategy(strategy)
            elif isinstance(question, RankingQuestion):
                strategy = RankingQuestionStrategy(strategy)
            elif isinstance(question, TextQuestion):
                strategy = TextQuestionStrategy(strategy)
            else:
                raise ValueError(f"Question {question} is not supported yet")

        strategy.unify_responses(self.records, question)
        return self

    # TODO(alvarobartt,davidberenstein1957): we should consider having something like
    # `export(..., training=True)` to export the dataset records in any format, replacing
    # both `format_as` and `prepare_for_training`
    def prepare_for_training(
        self,
        framework: Union[Framework, str],
        task: TrainingTaskTypes,
        train_size: Optional[float] = 1,
        test_size: Optional[float] = None,
        seed: Optional[int] = None,
        lang: Optional[str] = None,
    ) -> Any:
        """
        Prepares the dataset for training for a specific training framework and NLP task by splitting the dataset into train and test sets.

        Args:
            framework: the framework to use for training. Currently supported frameworks are: `transformers`, `peft`,
                `setfit`, `spacy`, `spacy-transformers`, `span_marker`, `spark-nlp`, `openai`, `trl`, `sentence-transformers`.
            task: the NLP task to use for training. Currently supported tasks are: `TrainingTaskForTextClassification`,
                `TrainingTaskForSFT`, `TrainingTaskForRM`, `TrainingTaskForPPO`, `TrainingTaskForDPO`, `TrainingTaskForSentenceSimilarity`.
            train_size: the size of the train set. If `None`, the whole dataset will be used for training.
            test_size: the size of the test set. If `None`, the whole dataset will be used for testing.
            seed: the seed to use for splitting the dataset into train and test sets.
            lang: the spaCy language to use for training. If `None`, the language of the dataset will be used.
        """
        if isinstance(framework, str):
            framework = Framework(framework)

        # validate train and test sizes
        if train_size is None:
            train_size = 1
        if test_size is None:
            test_size = 1 - train_size

        # check if all numbers are larger than 0
        if not [abs(train_size), abs(test_size)] == [train_size, test_size]:
            raise ValueError("`train_size` and `test_size` must be larger than 0.")
        # check if train sizes sum up to 1
        if not (train_size + test_size) == 1:
            raise ValueError("`train_size` and `test_size` must sum to 1.")

        if test_size == 0:
            test_size = None

        if len(self.records) < 1:
            raise ValueError(
                "No records found in the dataset. Make sure you add records to the"
                " dataset via the `FeedbackDataset.add_records()` method first."
            )

        local_dataset = self.pull()
        if isinstance(task, (TrainingTaskForTextClassification, TrainingTaskForSentenceSimilarity)):
            if task.formatting_func is None:
                # in sentence-transformer models we can train without labels
                if task.label:
                    local_dataset = local_dataset.unify_responses(
                        question=task.label.question, strategy=task.label.strategy
                    )
        elif isinstance(task, TrainingTaskForQuestionAnswering):
            if task.formatting_func is None:
                local_dataset = self.unify_responses(question=task.answer.name, strategy="disagreement")
        elif not isinstance(
            task,
            (
                TrainingTaskForSFT,
                TrainingTaskForRM,
                TrainingTaskForPPO,
                TrainingTaskForDPO,
                TrainingTaskForChatCompletion,
            ),
        ):
            raise ValueError(f"Training data {type(task)} is not supported yet")

        data = task._format_data(local_dataset)
        if framework in [
            Framework.TRANSFORMERS,
            Framework.SETFIT,
            Framework.SPAN_MARKER,
            Framework.PEFT,
        ]:
            return task._prepare_for_training_with_transformers(
                data=data, train_size=train_size, seed=seed, framework=framework
            )
        elif framework in [Framework.SPACY, Framework.SPACY_TRANSFORMERS]:
            require_dependencies("spacy")
            import spacy

            if lang is None:
                _LOGGER.warning("spaCy `lang` is not provided. Using `en`(English) as default language.")
                lang = spacy.blank("en")
            elif lang.isinstance(str):
                if len(lang) == 2:
                    lang = spacy.blank(lang)
                else:
                    lang = spacy.load(lang)
            return task._prepare_for_training_with_spacy(data=data, train_size=train_size, seed=seed, lang=lang)
        elif framework is Framework.SPARK_NLP:
            return task._prepare_for_training_with_spark_nlp(data=data, train_size=train_size, seed=seed)
        elif framework is Framework.OPENAI:
            return task._prepare_for_training_with_openai(data=data, train_size=train_size, seed=seed)
        elif framework is Framework.TRL:
            return task._prepare_for_training_with_trl(data=data, train_size=train_size, seed=seed)
        elif framework is Framework.TRLX:
            return task._prepare_for_training_with_trlx(data=data, train_size=train_size, seed=seed)
        elif framework is Framework.SENTENCE_TRANSFORMERS:
            return task._prepare_for_training_with_sentence_transformers(data=data, train_size=train_size, seed=seed)
        else:
            raise NotImplementedError(
                f"Framework {framework} is not supported. Choose from: {[e.value for e in Framework]}"
            )
