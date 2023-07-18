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
from typing import TYPE_CHECKING, Iterator, List, Literal, Optional, Union
from uuid import UUID

from argilla.client.feedback.constants import FETCHING_BATCH_SIZE
from argilla.client.feedback.integrations.huggingface import HuggingFaceDatasetMixin
from argilla.client.feedback.mixin import ArgillaDatasetMixin
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    FieldSchema,
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
)
from argilla.client.feedback.training.schemas import (
    TrainingTaskMappingForTextClassification,
)
from argilla.client.feedback.types import AllowedFieldTypes, AllowedQuestionTypes
from argilla.client.feedback.unification import (
    LabelQuestionStrategy,
    MultiLabelQuestionStrategy,
    RankingQuestionStrategy,
    RatingQuestionStrategy,
)
from argilla.client.models import Framework
from argilla.utils.dependency import require_version, requires_version

if TYPE_CHECKING:
    from datasets import Dataset

_LOGGER = logging.getLogger(__name__)


class FeedbackDataset(ArgillaDatasetMixin, HuggingFaceDatasetMixin):
    """Class to work with `FeedbackDataset`s either locally, or remotely (Argilla or HuggingFace Hub).

    Args:
        guidelines: contains the guidelines for annotating the dataset.
        fields: contains the fields that will define the schema of the records in the dataset.
        questions: contains the questions that will be used to annotate the dataset.

    Attributes:
        guidelines: contains the guidelines for annotating the dataset.
        fields: contains the fields that will define the schema of the records in the dataset.
        questions: contains the questions that will be used to annotate the dataset.
        records: contains the records of the dataset if any. Otherwise it is an empty list.
        argilla_id: contains the id of the dataset in Argilla, if it has been uploaded (via `self.push_to_argilla()`). Otherwise, it is `None`.

    Raises:
        TypeError: if `guidelines` is not a string.
        TypeError: if `fields` is not a list of `FieldSchema`.
        ValueError: if `fields` does not contain at least one required field.
        TypeError: if `questions` is not a list of `TextQuestion`, `RatingQuestion`,
            `LabelQuestion`, and/or `MultiLabelQuestion`.
        ValueError: if `questions` does not contain at least one required question.

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
        >>> dataset.add_records(
        ...     [
        ...         rg.FeedbackRecord(
        ...             fields={"text": "This is the first record", "label": "positive"},
        ...             responses=[{"values": {"question-1": {"value": "This is the first answer"}, "question-2": {"value": 5}}}],
        ...             external_id="entry-1",
        ...         ),
        ...     ]
        ... )
        >>> dataset.records
        [FeedbackRecord(fields={"text": "This is the first record", "label": "positive"}, responses=[ResponseSchema(user_id=None, values={"question-1": ValueSchema(value="This is the first answer"), "question-2": ValueSchema(value=5), "question-3": ValueSchema(value="positive"), "question-4": ValueSchema(value=["category-1"])})], external_id="entry-1")]
        >>> dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")
        >>> dataset.argilla_id
        "..."
        >>> dataset = rg.FeedbackDataset.from_argilla(argilla_id="...")
        >>> dataset.records
        [FeedbackRecord(fields={"text": "This is the first record", "label": "positive"}, responses=[ResponseSchema(user_id=None, values={"question-1": ValueSchema(value="This is the first answer"), "question-2": ValueSchema(value=5), "question-3": ValueSchema(value="positive"), "question-4": ValueSchema(value=["category-1"])})], external_id="entry-1")]
    """

    argilla_id: Optional[UUID] = None

    def __init__(
        self,
        *,
        fields: List[AllowedFieldTypes],
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
        if not isinstance(fields, list):
            raise TypeError(f"Expected `fields` to be a list, got {type(fields)} instead.")

        any_required = False
        unique_names = set()
        for field in fields:
            if not isinstance(field, FieldSchema):
                raise TypeError(f"Expected `fields` to be a list of `FieldSchema`, got {type(field)} instead.")
            if field.name in unique_names:
                raise ValueError(f"Expected `fields` to have unique names, got {field.name} twice instead.")
            unique_names.add(field.name)
            if not any_required and field.required:
                any_required = True
        if not any_required:
            raise ValueError("At least one `FieldSchema` in `fields` must be required (`required=True`).")
        self._fields = fields
        self._fields_schema = None

        if not isinstance(questions, list):
            raise TypeError(f"Expected `questions` to be a list, got {type(questions)} instead.")

        any_required = False
        unique_names = set()
        for question in questions:
            if not isinstance(question, AllowedQuestionTypes.__args__):
                raise TypeError(
                    "Expected `questions` to be a list of"
                    f" `{'`, `'.join([arg.__name__ for arg in AllowedQuestionTypes.__args__])}` got a"
                    f" question in the list with type {type(question)} instead."
                )
            if question.name in unique_names:
                raise ValueError(f"Expected `questions` to have unique names, got {question.name} twice instead.")
            unique_names.add(question.name)
            if not any_required and question.required:
                any_required = True
        if not any_required:
            raise ValueError("At least one question in `questions` must be required (`required=True`).")
        self._questions = questions

        if guidelines is not None:
            if not isinstance(guidelines, str):
                raise TypeError(
                    f"Expected `guidelines` to be either None (default) or a string, got {type(guidelines)} instead."
                )
            if len(guidelines) < 1:
                raise ValueError(
                    "Expected `guidelines` to be either None (default) or a non-empty string, minimum length is 1."
                )
        self.__guidelines = guidelines

        self._records: List[FeedbackRecord] = []
        self._new_records: List[FeedbackRecord] = []

    def __len__(self) -> int:
        """Returns the number of records in the dataset."""
        return len(self.records)

    def __getitem__(self, key: Union[slice, int]) -> Union[FeedbackRecord, List[FeedbackRecord]]:
        """Returns the record(s) at the given index(es).

        Args:
            key: the index(es) of the record(s) to return. Can either be a single index or a slice.

        Returns:
            Either the record of the given index, or a list with the records at the given indexes.
        """
        if len(self.records) < 1:
            raise RuntimeError(
                "In order to get items from `rg.FeedbackDataset` you need to either add"
                " them first with `add_records` or fetch them from Argilla or"
                " HuggingFace with `fetch_records`."
            )
        if isinstance(key, int) and len(self.records) < key:
            raise IndexError(f"This dataset contains {len(self)} records, so index {key} is out of range.")
        return self.records[key]

    def __del__(self) -> None:
        """When the dataset object is deleted, delete all the records as well to avoid memory leaks."""
        if hasattr(self, "_records") and self._records is not None:
            del self._records
        if hasattr(self, "_new_records") and self._new_records is not None:
            del self._new_records

    def __enter__(self) -> "FeedbackDataset":
        """Allows the dataset to be used as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """When the context manager is exited, delete all the records as well to avoid memory leaks."""
        self.__del__()

    @property
    def guidelines(self) -> str:
        """Returns the guidelines for annotating the dataset."""
        return self.__guidelines

    @guidelines.setter
    def guidelines(self, guidelines: str) -> None:
        """Sets the guidelines for annotating the dataset."""
        if not isinstance(guidelines, str):
            raise TypeError(f"Expected `guidelines` to be a string, got {type(guidelines)} instead.")
        self.__guidelines = guidelines

    @property
    def fields(self) -> List[AllowedFieldTypes]:
        """Returns the fields that define the schema of the records in the dataset."""
        return self._fields

    def field_by_name(self, name: str) -> AllowedFieldTypes:
        for field in self._fields:
            if field.name == name:
                return field
        raise ValueError(
            f"Field with name='{name}' not found, available field names are:"
            f" {', '.join(f.name for f in self._fields)}"
        )

    @property
    def questions(self) -> List[AllowedQuestionTypes]:
        """Returns the questions that will be used to annotate the dataset."""
        return self._questions

    def question_by_name(self, name: str) -> AllowedQuestionTypes:
        for question in self._questions:
            if question.name == name:
                return question
        raise ValueError(
            f"Question with name='{name}' not found, available question names are:"
            f" {', '.join(q.name for q in self._questions)}"
        )

    @property
    def records(self) -> List[FeedbackRecord]:
        """Returns the all the records in the dataset."""
        return self._records + self._new_records

    def iter(self, batch_size: Optional[int] = FETCHING_BATCH_SIZE) -> Iterator[List[FeedbackRecord]]:
        """Returns an iterator over the records in the dataset.

        Args:
            batch_size: the size of the batches to return. Defaults to 100.
        """
        for i in range(0, len(self.records), batch_size):
            yield self.records[i : i + batch_size]

    @requires_version("datasets")
    def format_as(self, format: Literal["datasets"]) -> "Dataset":
        """Formats the `FeedbackDataset` as a `datasets.Dataset` object.

        Args:
            format: the format to use to format the `FeedbackDataset`. Currently supported formats are:
                `datasets`.

        Returns:
            The `FeedbackDataset.records` formatted as a `datasets.Dataset` object.

        Raises:
            ValueError: if the provided format is not supported.

        Examples:
            >>> import argilla as rg
            >>> rg.init(...)
            >>> dataset = rg.FeedbackDataset.from_argilla(name="my-dataset")
            >>> huggingface_dataset = dataset.format_as("datasets")
        """
        if format == "datasets":
            return self._huggingface_format(self)
        raise ValueError(f"Unsupported format '{format}'.")

    def unify_responses(
        self,
        question: Union[str, LabelQuestion, MultiLabelQuestion, RatingQuestion],
        strategy: Union[
            str, LabelQuestionStrategy, MultiLabelQuestionStrategy, RatingQuestionStrategy, RankingQuestionStrategy
        ],
    ) -> None:
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
            else:
                raise ValueError(f"Question {question} is not supported yet")

        strategy.unify_responses(self.records, question)

    def prepare_for_training(
        self,
        framework: Union[Framework, str],
        task_mapping: TrainingTaskMappingForTextClassification,
        train_size: Optional[float] = 1,
        test_size: Optional[float] = None,
        seed: Optional[int] = None,
        fetch_records: bool = True,
        lang: Optional[str] = None,
    ):
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

        if fetch_records:
            self.fetch_records()

        if isinstance(task_mapping, TrainingTaskMappingForTextClassification):
            self.unify_responses(question=task_mapping.label.question, strategy=task_mapping.label.strategy)
        else:
            raise ValueError(f"Training data {type(task_mapping)} is not supported yet")

        data = task_mapping._format_data(self.records)
        if framework in [
            Framework.TRANSFORMERS,
            Framework.SETFIT,
            Framework.SPAN_MARKER,
            Framework.PEFT,
        ]:
            return task_mapping._prepare_for_training_with_transformers(
                data=data, train_size=train_size, seed=seed, framework=framework
            )
        elif framework is Framework.SPACY or framework is Framework.SPACY_TRANSFORMERS:
            require_version("spacy")
            import spacy

            if lang is None:
                _LOGGER.warning("spaCy `lang` is not provided. Using `en`(English) as default language.")
                lang = spacy.blank("en")
            elif lang.isinstance(str):
                if len(lang) == 2:
                    lang = spacy.blank(lang)
                else:
                    lang = spacy.load(lang)
            return task_mapping._prepare_for_training_with_spacy(data=data, train_size=train_size, seed=seed, lang=lang)
        elif framework is Framework.SPARK_NLP:
            return task_mapping._prepare_for_training_with_spark_nlp(data=data, train_size=train_size, seed=seed)
        elif framework is Framework.OPENAI:
            return task_mapping._prepare_for_training_with_openai(data=data, train_size=train_size, seed=seed)
        else:
            raise NotImplementedError(
                f"Framework {framework} is not supported. Choose from: {[e.value for e in Framework]}"
            )
