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
from abc import ABC, abstractproperty
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from pydantic import ValidationError

from argilla.client.feedback.integrations.huggingface import HuggingFaceDatasetMixin
from argilla.client.feedback.schemas import (
    FeedbackRecord,
    FieldSchema,
)
from argilla.client.feedback.schemas.types import AllowedMetadataPropertyTypes, AllowedQuestionTypes
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
from argilla.client.feedback.utils import generate_pydantic_schema_for_fields, generate_pydantic_schema_for_metadata
from argilla.client.models import Framework
from argilla.utils.dependency import require_dependencies, requires_dependencies

if TYPE_CHECKING:
    from datasets import Dataset

    from argilla.client.feedback.schemas.types import (
        AllowedFieldTypes,
        AllowedRemoteFieldTypes,
        AllowedRemoteMetadataPropertyTypes,
        AllowedRemoteQuestionTypes,
    )


_LOGGER = logging.getLogger(__name__)


class FeedbackDatasetBase(ABC, HuggingFaceDatasetMixin):
    """Base class with shared functionality for `FeedbackDataset` and `RemoteFeedbackDataset`."""

    def __init__(
        self,
        *,
        fields: Union[List["AllowedFieldTypes"], List["AllowedRemoteFieldTypes"]],
        questions: Union[List["AllowedQuestionTypes"], List["AllowedRemoteQuestionTypes"]],
        metadata_properties: Optional[
            Union[List["AllowedMetadataPropertyTypes"], List["AllowedRemoteMetadataPropertyTypes"]]
        ] = None,
        guidelines: Optional[str] = None,
        # TODO: uncomment once ready in the API
        # extra_metadata_allowed: bool = True,
    ) -> None:
        """Initializes a `FeedbackDatasetBase` instance locally.

        Args:
            fields: contains the fields that will define the schema of the records in the dataset.
            questions: contains the questions that will be used to annotate the dataset.
            metadata_properties: contains the metadata properties that will be indexed
                and could be used to filter the dataset. Defaults to `None`.
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

        if metadata_properties is not None:
            unique_names = set()
            for metadata_property in metadata_properties:
                if not isinstance(metadata_property, AllowedMetadataPropertyTypes.__args__):
                    raise TypeError(
                        f"Expected `metadata_properties` to be a list of"
                        f" `{'`, `'.join([arg.__name__ for arg in AllowedMetadataPropertyTypes.__args__])}` got a"
                        f" metadata property in the list with type type {type(metadata_property)} instead"
                    )
                if metadata_property.name in unique_names:
                    raise ValueError(
                        f"Expected `metadata_properties` to have unique names, got '{metadata_property.name}' twice instead."
                    )
                unique_names.add(metadata_property.name)
        self._metadata_properties = metadata_properties

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
        # TODO: uncomment once ready in the API
        # self._extra_metadata_allowed = extra_metadata_allowed

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
    def fields(self) -> Union[List["AllowedFieldTypes"], List["AllowedRemoteFieldTypes"]]:
        """Returns the fields that define the schema of the records in the dataset."""
        return self._fields

    def field_by_name(self, name: str) -> Union["AllowedFieldTypes", "AllowedRemoteFieldTypes"]:
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
    def questions(self) -> Union[List[AllowedQuestionTypes], List["AllowedRemoteQuestionTypes"]]:
        """Returns the questions that will be used to annotate the dataset."""
        return self._questions

    def question_by_name(self, name: str) -> Union[AllowedQuestionTypes, "AllowedRemoteQuestionTypes"]:
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

    @property
    def metadata_properties(
        self,
    ) -> Union[List["AllowedMetadataPropertyTypes"], List["AllowedRemoteMetadataPropertyTypes"]]:
        """Returns the metadata properties that will be indexed and could be used to filter the dataset."""
        return self._metadata_properties

    def metadata_property_by_name(
        self, name: str
    ) -> Union["AllowedMetadataPropertyTypes", "AllowedRemoteMetadataPropertyTypes"]:
        """Returns the metadata property by name if it exists. Othewise a `ValueError` is raised.

        Args:
            name: the name of the metadata property to return.

        Raises:
            ValueError: if the metadata property with the given name does not exist.
        """
        for metadata_property in self._metadata_properties:
            if metadata_property.name == name:
                return metadata_property
        raise ValueError(
            f"Metadata property with name='{name}' not found, available metadata property names are:"
            f" {', '.join(m.name for m in self._metadata_properties)}"
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
            self._fields_schema = generate_pydantic_schema_for_fields(self.fields)

        # TODO: this is here to avoid conflicts with other PRs
        if not hasattr(self, "_metadata_schema"):
            self._metadata_schema = None

        if self._metadata_schema is None:
            self._metadata_schema = generate_pydantic_schema_for_metadata(self.metadata_properties)

        for record in records:
            try:
                self._fields_schema.parse_obj(record.fields)
            except ValidationError as e:
                raise ValueError(
                    f"`FeedbackRecord.fields` does not match the expected schema, with exception: {e}"
                ) from e

            if record.metadata is not None and self.metadata_properties is not None:
                try:
                    self._metadata_schema.parse_obj(record.metadata)
                except ValidationError as e:
                    raise ValueError(
                        f"`FeedbackRecord.metadata` does not match the expected schema, with exception: {e}"
                    ) from e

    def _parse_and_validate_records(
        self,
        records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]],
    ) -> List[FeedbackRecord]:
        """Convenient method for calling `_parse_records` and `_validate_records` in sequence."""
        records = self._parse_records(records)
        self._validate_records(records)
        return records

    @requires_dependencies("datasets")
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
                " dataset via the `FeedbackDataset.add_records` method first."
            )

        if isinstance(task, (TrainingTaskForTextClassification, TrainingTaskForSentenceSimilarity)):
            if task.formatting_func is None:
                # in sentence-transformer models we can train without labels
                if task.label:
                    self.unify_responses(question=task.label.question, strategy=task.label.strategy)
        elif isinstance(task, TrainingTaskForQuestionAnswering):
            if task.formatting_func is None:
                self.unify_responses(question=task.answer.name, strategy="disagreement")
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

        data = task._format_data(self)
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
