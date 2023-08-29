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

import warnings
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Generic, Iterator, List, Optional, Type, TypeVar, Union

from argilla.client.feedback.dataset.base import FeedbackDatasetBase
from argilla.client.feedback.dataset.remote.mixins import ArgillaRecordsMixin
from argilla.client.feedback.schemas.records import RemoteFeedbackRecord, RemoteSuggestionSchema
from argilla.client.sdk.users.models import UserRole
from argilla.client.utils import allowed_for_roles

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla.client.feedback.dataset.local import FeedbackDataset
    from argilla.client.feedback.schemas.records import FeedbackRecord
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes
    from argilla.client.sdk.v1.datasets.models import FeedbackItemModel, FeedbackRecordsModel
    from argilla.client.workspaces import Workspace


warnings.simplefilter("always", DeprecationWarning)

T = TypeVar("T", bound="RemoteFeedbackRecordsBase")


class RemoteFeedbackRecordsBase(ABC, ArgillaRecordsMixin):
    def __init__(self, dataset: "RemoteFeedbackDatasetBase") -> None:
        """Initializes a `RemoteFeedbackRecords` instance to access a `FeedbackDataset`
        records in Argilla. This class is used to get records from Argilla, iterate over
        them, and push new records to Argilla.

        Note:
            This class is not intended to be initiallised directly. Instead, use
            `FeedbackDataset.from_argilla` to get an instance of `RemoteFeedbackDataset`,
            and then just call `records` on it.

        Args:
            dataset: the `RemoteFeedbackDataset` instance to access the `httpx.Client`,
                the ID of the dataset in Argilla, and everything else to reuse some methods
                and/or attributes.
        """
        self._dataset = dataset
        self._client = self._dataset._client  # Required to be able to use `allowed_for_roles` decorator

        self.__question_id2name = {question.id: question.name for question in self._dataset.questions}
        self.__question_name2id = {value: key for key, value in self.__question_id2name.items()}

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def __repr__(self) -> str:
        """Doesn't return anything, but prints a warning, since the `records` of a
        `FeedbackDataset` in Argilla are being lazily fetched, and never stored
        locally."""
        warnings.warn(
            "The `records` of a `FeedbackDataset` in Argilla are being lazily"
            " fetched, and never stored locally. You can either loop over `records`"
            " or access them by index, and those will be fetched from Argilla on the"
            " fly.",
            stacklevel=1,
        )
        return f"[{','.join([str(record) for record in self][:2])}, ...]"

    def _parse_record(self, record: "FeedbackItemModel") -> RemoteFeedbackRecord:
        """Parses a `FeedbackItemModel` into a `RemoteFeedbackRecord`."""
        suggestions = []
        if record.suggestions is not None:
            for suggestion in record.suggestions:
                suggestions.append(
                    RemoteSuggestionSchema(
                        client=self._client,
                        record_id=record.id,
                        question_name=self.__question_id2name[suggestion.question_id],
                        **suggestion.dict(),
                    )
                )
        record = record.dict(
            exclude={
                "inserted_at": ...,
                "updated_at": ...,
                "responses": {"__all__": {"id", "inserted_at", "updated_at"}},
                "suggestions": ...,
            },
            exclude_none=True,
        )
        return RemoteFeedbackRecord(
            client=self._client, name2id=self.__question_name2id, suggestions=suggestions, **record
        )

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def _fetch_records(self, offset: int, limit: int) -> "FeedbackRecordsModel":
        pass

    @abstractmethod
    def add(self) -> None:
        pass

    @abstractmethod
    def delete(self) -> None:
        pass


class RemoteFeedbackDatasetBase(Generic[T], FeedbackDatasetBase):
    records_cls: Type[T]

    def __init__(
        self,
        *,
        client: "httpx.Client",
        id: "UUID",
        name: str,
        workspace: "Workspace",
        fields: List["AllowedFieldTypes"],
        questions: List["AllowedQuestionTypes"],
        guidelines: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initializes a `RemoteFeedbackDataset` instance in Argilla.

        Note:
            This class is not intended to be initiallised directly. Instead, use
            `FeedbackDataset.from_argilla` to get an instance of this class.

        Args:
            client: contains the `httpx.Client` instance that will be used to send requests to Argilla.
            id: contains the UUID of the dataset in Argilla.
            name: contains the name of the dataset in Argilla.
            workspace: contains the `Workspace` instance that the dataset belongs to in Argilla.
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
        super().__init__(fields=fields, questions=questions, guidelines=guidelines)

        self._client = client  # Required to be able to use `allowed_for_roles` decorator
        self._id = id
        self._name = name
        self._workspace = workspace

        self._records = self.records_cls(dataset=self, **kwargs)

    @property
    def records(self) -> T:
        """Returns an instance of `RemoteFeedbackRecords` that allows you to iterate over
        the records in the dataset. The records are fetched from Argilla on the fly and
        not stored in memory. You can also iterate over the records directly from the
        dataset instance.
        """
        return self._records

    @property
    def argilla_id(self) -> "UUID":
        warnings.warn(
            "`argilla_id` is deprected in favor of `id` and will be removed in a future"
            " release. Please use `id` instead.\n`argilla_id` will be deprecated in"
            " Argilla v1.15.0.",
            DeprecationWarning,
            stacklevel=1,
        )
        return self.id

    @property
    def id(self) -> "UUID":
        """Returns the ID of the dataset in Argilla."""
        return self._id

    @property
    def name(self) -> str:
        """Returns the name of the dataset in Argilla."""
        return self._name

    @property
    def workspace(self) -> "Workspace":
        """Returns the workspace the dataset belongs to in Argilla."""
        return self._workspace

    @property
    def url(self) -> str:
        """Returns the URL of the dataset in Argilla."""
        return f"{self._client.base_url}/dataset/{self.id}/annotation-mode"

    def __repr__(self) -> str:
        """Returns a string representation of the dataset."""
        return (
            f"<FeedbackDataset id={self.id} name={self.name} workspace={self.workspace}"
            f" url={self.url} fields={self.fields} questions={self.questions}"
            f" guidelines={self.guidelines}>"
        )

    def __len__(self) -> int:
        """Returns the number of records in the dataset."""
        return self._records.__len__()

    def __iter__(self) -> Iterator[RemoteFeedbackRecord]:
        """Returns an iterator over the records in the dataset."""
        yield from self._records

    def __getitem__(self, key: Union[slice, int]) -> Union[RemoteFeedbackRecord, List[RemoteFeedbackRecord]]:
        """Returns the record(s) at the given index(es).

        Args:
            key: The index or slice to retrieve.

        Returns:
            The record(s) at the given index(es).
        """
        return self._records.__getitem__(key)

    def add_records(
        self,
        records: Union["FeedbackRecord", Dict[str, Any], List[Union["FeedbackRecord", Dict[str, Any]]]],
        show_progress: bool = True,
    ) -> None:
        """Adds the given records to the dataset and pushes those to Argilla.

        Args:
            records: can be a single `FeedbackRecord`, a list of `FeedbackRecord`,
                a single dictionary, or a list of dictionaries. If a dictionary is provided,
                it will be converted to a `FeedbackRecord` internally.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            ValueError: if the given records are neither: `FeedbackRecord`, list of
                `FeedbackRecord`, list of dictionaries as a record or dictionary as a
                record; or if the given records do not match the expected schema.
        """
        self._records.add(records=records, show_progress=show_progress)

    def delete_records(self, records: Union["RemoteFeedbackRecord", List["RemoteFeedbackRecord"]]) -> None:
        """Deletes the given records from the dataset in Argilla.

        Args:
            records: the records to delete from the dataset. Can be a single record or a list
                of records. But those need to be previously pushed to Argilla, otherwise
                they won't be deleted.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            RuntimeError: If the deletion of the records from Argilla fails.
        """
        self._records.delete(records=[records] if not isinstance(records, list) else records)

    def fetch_records(self) -> None:
        warnings.warn(
            "`fetch_records` method is deprecated, as the records are fetched automatically"
            " when iterating over a `FeedbackDataset` pushed to Argilla.\n`fetch_records`"
            " will be deprecated in Argilla v1.15.0.",
            DeprecationWarning,
            stacklevel=1,
        )

    def push_to_argilla(self, *args, **kwargs) -> None:
        warnings.warn(
            "`push_to_argilla` is no longer working for a `FeedbackDataset` pushed to Argilla,"
            " as the additions, deletions and/or updates over a `FeedbackDataset` in Argilla"
            " are being tracked automatically, so there's no need to explicitly push them."
            "\n`push_to_argilla` will be deprecated in Argilla v1.15.0.",
            DeprecationWarning,
            stacklevel=1,
        )

    def pull(self) -> "FeedbackDataset":
        """Pulls the dataset from Argilla and returns a local instance of it.

        Returns:
            A local instance of the dataset which is a `FeedbackDataset` object.
        """
        # Importing here to avoid circular imports
        from argilla.client.feedback.dataset.local import FeedbackDataset

        instance = FeedbackDataset(
            fields=self.fields,
            questions=self.questions,
            guidelines=self.guidelines,
        )
        instance.add_records(
            records=[
                record.dict(
                    exclude={
                        "id": ...,
                        "client": ...,
                        "name2id": ...,
                        "suggestions": {"__all__": {"client", "id", "record_id", "question_id"}},
                    },
                    exclude_none=True,
                )
                for record in self._records
            ],
        )
        return instance
