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

from abc import ABC, ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from pydantic import ValidationError

from argilla.client.feedback.integrations.huggingface import HuggingFaceDatasetMixin
from argilla.client.feedback.schemas import (
    FeedbackRecord,
)
from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes
from argilla.client.feedback.utils import generate_pydantic_schema
from argilla.utils.dependency import requires_dependencies

if TYPE_CHECKING:
    from datasets import Dataset

    from argilla.client.feedback.schemas.types import (
        AllowedRemoteFieldTypes,
        AllowedRemoteQuestionTypes,
    )


class FeedbackDatasetBase(ABC, HuggingFaceDatasetMixin, metaclass=ABCMeta):
    """Base class with shared functionality for `FeedbackDataset` and `RemoteFeedbackDataset`."""

    def __init__(
        self,
        *,
        fields: Union[List[AllowedFieldTypes], List["AllowedRemoteFieldTypes"]],
        questions: Union[List[AllowedQuestionTypes], List["AllowedRemoteQuestionTypes"]],
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
            if not isinstance(field, AllowedFieldTypes):
                raise TypeError(
                    f"Expected `fields` to be a list of `{AllowedFieldTypes.__name__}`, got {type(field)} instead."
                )
            if field.name in unique_names:
                raise ValueError(f"Expected `fields` to have unique names, got {field.name} twice instead.")
            unique_names.add(field.name)
            if not any_required and field.required:
                any_required = True

        if not any_required:
            raise ValueError("At least one field in `fields` must be required (`required=True`).")

        self._fields = fields
        self._fields_schema = generate_pydantic_schema(self.fields)

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
    @abstractmethod
    def records(self) -> Any:
        """Returns the records of the dataset."""
        pass

    @property
    def guidelines(self) -> str:
        """Returns the guidelines for annotating the dataset."""
        return self._guidelines

    @property
    def fields(self) -> Union[List[AllowedFieldTypes], List["AllowedRemoteFieldTypes"]]:
        """Returns the fields that define the schema of the records in the dataset."""
        return self._fields

    def field_by_name(self, name: str) -> Union[AllowedFieldTypes, "AllowedRemoteFieldTypes"]:
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

    @abstractmethod
    def add_records(self, *args, **kwargs) -> None:
        """Adds the given records to the `FeedbackDataset`."""
        pass

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

    @abstractmethod
    def pull(self):
        """Pulls the dataset from Argilla and returns a local instance of it."""
        pass

    @abstractmethod
    def filter_by(self, *args, **kwargs):
        """Filters the current `FeedbackDataset`."""
        pass

    @abstractmethod
    def delete(self):
        """Deletes the `FeedbackDataset` from Argilla."""
        pass

    @abstractmethod
    def prepare_for_training(self, *args, **kwargs) -> Any:
        """Prepares the `FeedbackDataset` for training by creating the training."""
        pass

    @abstractmethod
    def push_to_argilla(self, *args, **kwargs) -> "FeedbackDatasetBase":
        """Pushes the `FeedbackDataset` to Argilla."""
        pass

    @abstractmethod
    def unify_responses(self, *args, **kwargs):
        """Unifies the responses for a given question."""
        pass
