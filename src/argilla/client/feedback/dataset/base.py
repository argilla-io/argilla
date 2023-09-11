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
from abc import ABC, abstractmethod, abstractproperty
from typing import TYPE_CHECKING, Any, Dict, List, Union

from argilla.client.feedback.schemas import (
    FeedbackRecord,
)
from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes

if TYPE_CHECKING:
    pass


_LOGGER = logging.getLogger(__name__)


class FeedbackDatasetSharedBase(ABC):
    """Base class with shared functionality and required methods for `FeedbackDataset` and `RemoteFeedbackDataset`."""

    @property
    @abstractproperty
    def __len__(self) -> None:
        """Returns the number of records in the dataset."""

    @property
    @abstractproperty
    def __repr__(self) -> None:
        """Returns a string representation of the dataset."""

    @property
    @abstractproperty
    def __getitem__(self) -> None:
        """Returns the record(s) at the given index(es)."""

    def __iter__(self):
        """Returns an iterator over the records in the dataset."""
        yield from self._records

    @abstractmethod
    def iter(self) -> Any:
        """Returns an iterator over the records in the dataset."""

    @property
    @abstractproperty
    def records(self) -> Any:
        """Returns the records of the dataset."""

    @property
    @abstractproperty
    def guidelines(self) -> str:
        """Returns the guidelines for annotating the dataset."""

    @property
    @abstractproperty
    def fields(self) -> List[AllowedFieldTypes]:
        """Returns the fields that define the schema of the records in the dataset."""

    def field_by_name(self, name: str) -> AllowedFieldTypes:
        """Returns the field by name if it exists. Othewise a `ValueError` is raised.

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
    @abstractproperty
    def questions(self) -> List[AllowedQuestionTypes]:
        """Returns the questions that will be used to annotate the dataset."""

    def question_by_name(self, name: str) -> AllowedQuestionTypes:
        """Returns the question by name if it exists. Othewise a `ValueError` is raised.

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

    @abstractmethod
    def _parse_records(
        self, records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]]
    ) -> List[FeedbackRecord]:
        """Parses the records into a list of `FeedbackRecord` objects."""

    @abstractmethod
    def delete(self) -> None:
        """Deletes a dataset."""

    def add(self) -> Any:
        """Adds records to the dataset."""
        warnings.warn(
            "`add` will be deprecated in future versions. Use `add_records` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.add_records()

    @abstractmethod
    def add_records(self) -> Any:
        """Adds records to the dataset."""

    @abstractmethod
    def delete_records(self) -> Any:
        """Adds records to the dataset."""

    @abstractmethod
    def filter_by(self) -> Any:
        """Adds records to the dataset."""

    def pull(self) -> "FeedbackDataset":
        """`pull` will be deprecated in future versions. Use `pull_from_argilla` instead."""
        warnings.warn(
            "`pull` will be deprecated in future versions. Use `pull_from_argilla` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.pull_from_argilla()

    @abstractmethod
    def pull_from_argilla(self) -> Any:
        """ "Pulls the dataset from Argilla and returns a local instance of it."""

    @abstractmethod
    def push_to_argilla(self) -> Any:
        """`push_to_argilla` doesn't work for neither `RemoteFeedbackDataset` nor `FilteredRemoteFeedbackDataset`."""

    @abstractmethod
    def prepare_for_training(self) -> Any:
        """Prepares the dataset for training."""
