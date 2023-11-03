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
from typing import TYPE_CHECKING, Any, Dict, Generic, Iterable, List, Literal, Optional, Type, TypeVar, Union

from pydantic import BaseModel, ValidationError

from argilla.client.feedback.dataset import helpers
from argilla.client.feedback.integrations.huggingface import HuggingFaceDatasetMixin
from argilla.client.feedback.schemas.records import FeedbackRecord, SortBy
from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedMetadataPropertyTypes, AllowedQuestionTypes
from argilla.client.feedback.schemas.vector_settings import VectorSettings
from argilla.client.feedback.utils import generate_pydantic_schema_for_fields, generate_pydantic_schema_for_metadata
from argilla.utils.dependency import requires_dependencies

if TYPE_CHECKING:
    from datasets import Dataset

    from argilla.client.feedback.schemas.types import (
        AllowedRemoteFieldTypes,
        AllowedRemoteMetadataPropertyTypes,
        AllowedRemoteQuestionTypes,
    )

R = TypeVar("R", bound=FeedbackRecord)


class FeedbackDatasetBase(ABC, Generic[R], metaclass=ABCMeta):
    """Base class with shared functionality for `FeedbackDataset` and `RemoteFeedbackDataset`."""

    def __init__(
        self,
        *,
        fields: Union[List[AllowedFieldTypes], List["AllowedRemoteFieldTypes"]],
        questions: Union[List[AllowedQuestionTypes], List["AllowedRemoteQuestionTypes"]],
        metadata_properties: Optional[
            Union[List["AllowedMetadataPropertyTypes"], List["AllowedRemoteMetadataPropertyTypes"]]
        ] = None,
        guidelines: Optional[str] = None,
        allow_extra_metadata: bool = True,
    ) -> None:
        """Initializes a `FeedbackDatasetBase` instance locally.

        Args:
            fields: contains the fields that will define the schema of the records in the dataset.
            questions: contains the questions that will be used to annotate the dataset.
            metadata_properties: contains the metadata properties that will be indexed
                and could be used to filter the dataset. Defaults to `None`.
            guidelines: contains the guidelines for annotating the dataset. Defaults to `None`.
            allow_extra_metadata: whether to allow extra metadata that has not been defined
                as a metadata property in the records. Defaults to `True`.

        Raises:
            TypeError: if `fields` is not a list of `FieldSchema`.
            ValueError: if `fields` does not contain at least one required field.
            TypeError: if `questions` is not a list of `TextQuestion`, `RatingQuestion`,
                `LabelQuestion`, and/or `MultiLabelQuestion`.
            ValueError: if `questions` does not contain at least one required question.
            TypeError: if `guidelines` is not None and not a string.
            ValueError: if `guidelines` is an empty string.
        """

        helpers.validate_fields(fields)
        helpers.validate_questions(questions)
        helpers.validate_metadata_properties(metadata_properties)

        if guidelines is not None:
            if not isinstance(guidelines, str):
                raise TypeError(
                    f"Expected `guidelines` to be either None (default) or a string, got {type(guidelines)} instead."
                )
            if len(guidelines) < 1:
                raise ValueError(
                    "Expected `guidelines` to be either None (default) or a non-empty string, minimum length is 1."
                )

        self._fields = fields or []
        self._questions = questions or []
        self._metadata_properties = metadata_properties or []
        self._guidelines = guidelines
        self._allow_extra_metadata = allow_extra_metadata

    @property
    @abstractmethod
    def records(self) -> Iterable[R]:
        """Returns the records of the dataset."""
        pass

    @abstractmethod
    def update_records(self, records: Union[R, List[R]]) -> None:
        """Updates the records of the dataset.

        Args:
            records: the records to update the dataset with.

        Raises:
            ValueError: if the provided `records` are invalid.
        """
        pass

    @property
    def guidelines(self) -> str:
        """Returns the guidelines for annotating the dataset."""
        return self._guidelines

    @property
    def allow_extra_metadata(self) -> bool:
        """Returns whether if adding extra metadata to the records of the dataset is allowed"""
        return self._allow_extra_metadata

    @property
    def fields(self) -> Union[List[AllowedFieldTypes], List["AllowedRemoteFieldTypes"]]:
        """Returns the fields that define the schema of the records in the dataset."""
        return self._fields

    def field_by_name(self, name: str) -> Union[AllowedFieldTypes, "AllowedRemoteFieldTypes"]:
        """Returns the field by name if it exists. Otherwise a `ValueError` is raised.

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
        """Returns the question by name if it exists. Otherwise a `ValueError` is raised.

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
        """Returns the metadata property by name if it exists. Otherwise a `ValueError` is raised.

        Args:
            name: the name of the metadata property to return.

        Raises:
            KeyError: if the metadata property with the given name does not exist.
        """
        existing_metadata_properties = self.metadata_properties
        if not existing_metadata_properties:
            raise ValueError(
                "The current `FeedbackDataset` has no `metadata_properties` defined, please add them first via"
                " `FeedbackDataset.add_metadata_property`."
            )

        for metadata_property in existing_metadata_properties:
            if metadata_property.name == name:
                return metadata_property

        raise KeyError(
            f"Metadata property with name='{name}' not found, available metadata property names are:"
            f" {', '.join([metadata_property.name for metadata_property in existing_metadata_properties])}"
        )

    @abstractmethod
    def vector_settings_by_name(self, name: str) -> "VectorSettings":
        """Returns the vector settings by name if it exists. Otherwise a `ValueError` is raised.

        Args:
            name: the name of the vector settings to return.

        Raises:
            KeyError: if the vector settings with the given name does not exist.
        """
        pass

    @abstractmethod
    def sort_by(self, sort: List[SortBy]) -> "FeedbackDatasetBase":
        """Sorts the records in the dataset by the given field."""
        pass

    def _build_fields_schema(self) -> Type[BaseModel]:
        """Returns the fields schema of the dataset."""
        return generate_pydantic_schema_for_fields(self.fields)

    def _build_metadata_schema(self) -> Type[BaseModel]:
        """Returns the metadata schema of the dataset."""
        return generate_pydantic_schema_for_metadata(
            self.metadata_properties, allow_extra_metadata=self.allow_extra_metadata
        )

    def _unique_metadata_property(self, metadata_property: "AllowedMetadataPropertyTypes") -> None:
        """Checks whether the provided `metadata_property` already exists in the dataset.

        Args:
            metadata_property: the metadata property to validate.

        Raises:
            ValueError: if the `metadata_property` already exists in the dataset.
        """
        existing_metadata_properties = self.metadata_properties
        if existing_metadata_properties:
            existing_metadata_property_names = [
                metadata_property.name for metadata_property in existing_metadata_properties
            ]
            if metadata_property.name in existing_metadata_property_names:
                raise ValueError(
                    f"Invalid `metadata_property={metadata_property.name}` provided as it already exists. Current"
                    f" `metadata_properties` are: {', '.join(existing_metadata_property_names)}"
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

    def _validate_records(
        self, records: List[FeedbackRecord], attributes_to_validate: Optional[List[str]] = None
    ) -> None:
        """Validates the records against the schema defined by the `fields`.

        Args:
            records: a list of `FeedbackRecord` objects to validate.
            attributes_to_validate: a list containing the name of the attributes to
                validate from the record. Valid values are: `fields` and `metadata`.
                If not provided, both `fields` and `metadata` are validated. Defaults
                to `None`.

        Raises:
            ValueError: if the `fields` schema does not match the `FeedbackRecord.fields` schema.
        """
        if attributes_to_validate is None:
            attributes_to_validate = ["fields", "metadata"]

        if "fields" in attributes_to_validate:
            fields_schema = self._build_fields_schema()

        if "metadata" in attributes_to_validate:
            metadata_schema = self._build_metadata_schema()

        for record in records:
            if "fields" in attributes_to_validate:
                self._validate_record_fields(record, fields_schema)

            if "metadata" in attributes_to_validate:
                self._validate_record_metadata(record, metadata_schema)

            # TODO: Add validation of vectors using vector_settings.

    @staticmethod
    def _validate_record_fields(record: FeedbackRecord, fields_schema: Type[BaseModel]) -> None:
        """Validates the `FeedbackRecord.fields` against the schema defined by the `fields`."""
        try:
            fields_schema.parse_obj(record.fields)
        except ValidationError as e:
            raise ValueError(f"`FeedbackRecord.fields` does not match the expected schema, with exception: {e}") from e

    def _validate_record_metadata(self, record: FeedbackRecord, metadata_schema: Type[BaseModel] = None) -> None:
        """Validates the `FeedbackRecord.metadata` against the schema defined by the `metadata_properties`."""

        if not record.metadata:
            return

        try:
            metadata_schema.parse_obj(record.metadata)
        except ValidationError as e:
            raise ValueError(
                f"`FeedbackRecord.metadata` {record.metadata} does not match the expected schema,"
                f" with exception: {e}"
            ) from e

    def _parse_and_validate_records(
        self,
        records: Union[R, Dict[str, Any], List[Union[R, Dict[str, Any]]]],
    ) -> List[R]:
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
            return HuggingFaceDatasetMixin._huggingface_format(self)
        raise ValueError(f"Unsupported format '{format}'.")

    @abstractmethod
    def add_records(self, *args, **kwargs) -> None:
        """Adds the given records to the `FeedbackDataset`."""
        pass

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

    @abstractmethod
    def add_metadata_property(self, *args, **kwargs):
        """Adds a new `metadata_property` to the current `FeedbackDataset`."""
        pass

    @abstractmethod
    def update_metadata_properties(self, *args, **kwargs):
        """Updates the `metadata_properties` of the current `FeedbackDataset`."""
        pass

    @abstractmethod
    def delete_metadata_properties(self, *args, **kwargs):
        """Deletes a list of `metadata_properties` from the current `FeedbackDataset`."""
        pass

    @abstractmethod
    def add_vector_settings(self, *args, **kwargs):
        """Adds a new `vector_settings` to the current `FeedbackDataset`."""
        pass

    @abstractmethod
    def update_vector_settings(self, *args, **kwargs):
        """Updates the `vector_settings` of the current `FeedbackDataset`."""
        pass

    @abstractmethod
    def delete_vector_settings(self, *args, **kwargs):
        """Deletes a list of `vector_settings` from the current `FeedbackDataset`."""
        pass

    @abstractmethod
    def push_to_huggingface(self, repo_id, generate_card, *args, **kwargs):
        """Pushes the current `FeedbackDataset` to HuggingFace Hub.

        Note:
            The records from the `RemoteFeedbackDataset` are being pulled before pushing,
            to ensure that there's no missmatch while uploading those as those are lazily fetched.

        Args:
            repo_id: the ID of the HuggingFace repo to push the dataset to.
            generate_card: whether to generate a dataset card or not. Defaults to `True`.
        """
        pass
