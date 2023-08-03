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
import warnings
from abc import ABC, abstractproperty
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from pydantic import ValidationError

from argilla.client.feedback.integrations.huggingface import HuggingFaceDatasetMixin
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    FieldSchema,
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
)
from argilla.client.feedback.training.schemas import TrainingTaskMappingForTextClassification
from argilla.client.feedback.types import AllowedFieldTypes, AllowedQuestionTypes
from argilla.client.feedback.unification import (
    LabelQuestionStrategy,
    MultiLabelQuestionStrategy,
    RankingQuestionStrategy,
    RatingQuestionStrategy,
)
from argilla.client.feedback.utils import generate_pydantic_schema
from argilla.client.models import Framework
from argilla.utils.dependency import require_version, requires_version

if TYPE_CHECKING:
    from datasets import Dataset


_LOGGER = logging.getLogger(__name__)


class FeedbackDatasetBase(ABC, HuggingFaceDatasetMixin):
    """Base class with shared functionality for `FeedbackDataset` and `RemoteFeedbackDataset`."""

    def __init__(
        self,
        *,
        fields: List[AllowedFieldTypes],
        questions: List[AllowedQuestionTypes],
        guidelines: Optional[str] = None,
    ) -> None:
        """Initializes a `FeedbackDatasetBase` instance locally.

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
        self._guidelines = guidelines

    @property
    @abstractproperty
    def records(self) -> Any:
        """Returns the records of the dataset."""
        pass

    @property
    def guidelines(self) -> str:
        """Returns the guidelines for annotating the dataset."""
        return self._guidelines

    @property
    def fields(self) -> List[AllowedFieldTypes]:
        """Returns the fields that define the schema of the records in the dataset."""
        return self._fields

    def field_by_name(self, name: str) -> AllowedFieldTypes:
        """Returns the field by name if it exists. Othewise a `ValueError` is raised.

        Args:
            name: the name of the field to return.

        Raises:
            ValueError: if the field with the given name does not exist.
        """
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
        """Returns the question by name if it exists. Othewise a `ValueError` is raised.

        Args:
            name: the name of the question to return.

        Raises:
            ValueError: if the question with the given name does not exist.
        """
        for question in self._questions:
            if question.name == name:
                return question
        raise ValueError(
            f"Question with name='{name}' not found, available question names are:"
            f" {', '.join(q.name for q in self._questions)}"
        )

    def _parse_records(
        self, records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]]
    ) -> List[FeedbackRecord]:
        """Parses the records into a list of `FeedbackRecord` objects.

        Args:
            records: either a single `FeedbackRecord` or `dict` or a list of `FeedbackRecord` or `dict`.

        Returns:
            A list of `FeedbackRecord` objects.

        Raises:
            ValueError: if `records` is not a `FeedbackRecord` or `dict` or a list of `FeedbackRecord` or `dict`.
        """
        if isinstance(records, (dict, FeedbackRecord)):
            records = [records]

        if len(records) == 0:
            raise ValueError("Expected `records` to be a non-empty list of `dict` or `FeedbackRecord`.")

        new_records = []
        for record in records:
            if isinstance(record, dict):
                new_records.append(FeedbackRecord(**record))
            elif isinstance(record, FeedbackRecord):
                new_records.append(record)
            else:
                raise ValueError(
                    "Expected `records` to be a list of `dict` or `FeedbackRecord`,"
                    f" got type `{type(record)}` instead."
                )
        return new_records

    def _validate_records(self, records: List[FeedbackRecord]) -> None:
        """Validates the records against the schema defined by the `fields`.

        Args:
            records: a list of `FeedbackRecord` objects to validate.

        Raises:
            ValueError: if the `fields` schema does not match the `FeedbackRecord.fields` schema.
        """
        if self._fields_schema is None:
            self._fields_schema = generate_pydantic_schema(self.fields)

        for record in records:
            try:
                self._fields_schema.parse_obj(record.fields)
            except ValidationError as e:
                raise ValueError(
                    f"`FeedbackRecord.fields` does not match the expected schema, with exception: {e}"
                ) from e

    def _parse_and_validate_records(
        self,
        records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]],
    ) -> List[FeedbackRecord]:
        """Convenient method for calling `_parse_records` and `_validate_records` in sequence."""
        records = self._parse_records(records)
        self._validate_records(records)
        return records

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

    # TODO(davidberenstein1957): detatch unification into a mixin
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

    # TODO(alvarobartt,davidberenstein1957): we should consider having something like
    # `export(..., training=True)` to export the dataset records in any format, replacing
    # both `format_as` and `prepare_for_training`
    def prepare_for_training(
        self,
        framework: Union[Framework, str],
        task_mapping: TrainingTaskMappingForTextClassification,
        train_size: Optional[float] = 1,
        test_size: Optional[float] = None,
        seed: Optional[int] = None,
        lang: Optional[str] = None,
        fetch_records: Optional[bool] = None,
    ):
        # TODO(davidberenstein1957): add missing docstrings and type annotations
        if fetch_records is not None:
            warnings.warn(
                "`fetch_records` is deprecated and will be removed in a future version."
                " `records` will be fetched automatically from Argilla, if the dataset"
                " is not in Argilla, then the local records will be used instead.\n`fetch_records`"
                " will be deprecated in Argilla v1.15.0.",
                DeprecationWarning,
                stacklevel=1,
            )

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
                " dataset via the `FeedbackDataset.add_records` method first."
            )

        if isinstance(task_mapping, TrainingTaskMappingForTextClassification):
            self.unify_responses(question=task_mapping.label.question, strategy=task_mapping.label.strategy)
        else:
            raise ValueError(f"Training data {type(task_mapping)} is not supported yet")

        data = task_mapping._format_data([record for record in self.records])
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
