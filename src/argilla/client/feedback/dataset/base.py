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
from typing import Any, Dict, Generic, Iterable, List, Literal, Optional, TYPE_CHECKING, Tuple, TypeVar, Union

from argilla.client.feedback.dataset import helpers
from argilla.client.feedback.integrations.huggingface import HuggingFaceDatasetMixin
from argilla.client.feedback.schemas.records import FeedbackRecord, SortBy
from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedMetadataPropertyTypes, AllowedQuestionTypes
from argilla.client.feedback.schemas.vector_settings import VectorSettings
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

    @property
    @abstractmethod
    def records(self) -> Iterable[R]:
        """Returns the records of the dataset."""
        pass

    @property
    @abstractmethod
    def vectors_settings(self) -> List[VectorSettings]:
        """Returns the vector settings of the dataset."""
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
    @abstractmethod
    def guidelines(self) -> Optional[str]:
        """Returns the guidelines for annotating the dataset."""
        pass

    @property
    @abstractmethod
    def allow_extra_metadata(self) -> bool:
        """Returns whether if adding extra metadata to the records of the dataset is allowed"""
        pass

    @property
    @abstractmethod
    def fields(self) -> Union[List[AllowedFieldTypes]]:
        """Returns the fields that define the schema of the records in the dataset."""
        pass

    def field_by_name(self, name: str) -> Union[AllowedFieldTypes]:
        """Returns the field by name if it exists. Otherwise a `ValueError` is raised.

        Args:
            name: the name of the field to return.

        Raises:
            ValueError: if the field with the given name does not exist.
        """
        for field in self.fields:
            if field.name == name:
                return field
        raise ValueError(
            f"Field with name='{name}' not found, available field names are:"
            f" {', '.join(f.name for f in self.fields)}"
        )

    @property
    @abstractmethod
    def questions(self) -> Union[List[AllowedQuestionTypes]]:
        """Returns the questions that will be used to annotate the dataset."""
        pass

    def question_by_name(self, name: str) -> Union[AllowedQuestionTypes]:
        """Returns the question by name if it exists. Otherwise a `ValueError` is raised.

        Args:
            name: the name of the question to return.

        Raises:
            ValueError: if the question with the given name does not exist.
        """
        for question in self.questions:
            if question.name == name:
                return question
        raise ValueError(
            f"Question with name='{name}' not found, available question names are:"
            f" {', '.join(q.name for q in self.questions)}"
        )

    @property
    @abstractmethod
    def metadata_properties(self) -> Union[List["AllowedMetadataPropertyTypes"]]:
        """Returns the metadata properties that will be indexed and could be used to filter the dataset."""
        pass

    def metadata_property_by_name(self, name: str) -> Union["AllowedMetadataPropertyTypes"]:
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
    def update_vectors_settings(self, *args, **kwargs):
        """Updates a list of `vector_settings` from the current `FeedbackDataset`."""
        pass

    @abstractmethod
    def delete_vectors_settings(self, *args, **kwargs):
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

    @abstractmethod
    def find_similar_records(
        self,
        vector_name: str,
        value: Optional[List[float]] = None,
        record: Optional[R] = None,
        max_results: int = 50,
    ) -> List[Tuple[R, float]]:
        """Finds similar records to the given `record` or `value` for the given `vector_name`.

        Args:
            vector_name: a vector name to use for searching by similarity.
            value: an optional vector value to be used for searching by similarity.
            record: an optional record to be used for searching by similarity.
            max_results: the maximum number of results for the search.

        Returns:
            A list of tuples with each tuple including a record and a similarity score.
        """
        pass
