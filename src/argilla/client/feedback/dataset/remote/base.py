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
from typing import TYPE_CHECKING, Any, Dict, Generic, Iterator, List, Optional, Type, TypeVar, Union

from argilla.client.feedback.constants import FETCHING_BATCH_SIZE
from argilla.client.feedback.dataset.base import FeedbackDatasetBase
from argilla.client.feedback.schemas.records import RemoteFeedbackRecord
from argilla.client.sdk.users.models import UserRole
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.utils import allowed_for_roles

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla.client.feedback.dataset.local import FeedbackDataset
    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from argilla.client.feedback.dataset.remote.filtered import FilteredRemoteFeedbackDataset
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes
    from argilla.client.sdk.v1.datasets.models import FeedbackItemModel
    from argilla.client.workspaces import Workspace


warnings.simplefilter("always", DeprecationWarning)

T = TypeVar("T")


class RemoteFeedbackRecordsBase:
    def __init__(self, dataset: Union["RemoteFeedbackDataset", "FilteredRemoteFeedbackDataset"]) -> None:
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
        self._dataset_id = self._dataset.id
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
        record = record.dict(
            exclude={
                "inserted_at": ...,
                "updated_at": ...,
                "responses": {"__all__": {"id", "inserted_at", "updated_at"}},
                "suggestions": {"__all__": {"id"}},
            },
            exclude_none=True,
        )
        for suggestion in record.get("suggestions", []):
            suggestion.update({"question_name": self.__question_id2name[suggestion["question_id"]]})
        return RemoteFeedbackRecord(client=self._client, name2id=self.__question_name2id, **record)

    # TODO(alvarobartt): use `response_status` filter when it's implemented in the API by @gabrielmbmb
    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def __len__(self) -> int:
        """Returns the number of records in the current `FeedbackDataset` in Argilla."""
        try:
            response = datasets_api_v1.get_metrics(client=self._client, id=self._dataset_id)
        except Exception as e:
            raise Exception(
                f"Failed while getting the metrics from the current `FeedbackDataset` in Argilla with exception: {e}"
            ) from e
        return response.parsed.records.count

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def _get_records(
        self, key: Union[slice, int], filters: Dict[str, Any] = {}
    ) -> Union[RemoteFeedbackRecord, List[RemoteFeedbackRecord]]:
        """Returns the record(s) at the given index(es) from Argilla.

        Args:
            key: the index(es) of the record(s) to return. Can either be a single index or a slice.

        Returns:
            Either the record of the given index, or a list with the records at the given indexes.
        """
        offsets = []
        limit = None
        num_records = len(self)
        if isinstance(key, slice):
            start, stop, step = key.indices(num_records)
            if step is not None and step != 1:
                raise ValueError("When providing a `slice` just `step=None` or `step=1` are allowed.")
            if start < 0:
                start += num_records
            if stop < 0:
                stop += num_records
            if start < 0 or stop < 0:
                raise IndexError(
                    f"Index {start if start < 0 else stop} is out of range, dataset has {num_records} records."
                )
            limit = stop - start
            if limit < 0:
                raise ValueError("Negative slice bounds are not supported.")
            elif limit < FETCHING_BATCH_SIZE:
                offsets = [start]
                limits = [limit]
            else:
                offsets = list(range(start, stop, FETCHING_BATCH_SIZE))
                limits = [FETCHING_BATCH_SIZE] * len(offsets)
                if stop % FETCHING_BATCH_SIZE != 0:
                    offsets[-1] = stop - (stop % FETCHING_BATCH_SIZE) + 1
                    limits[-1] = (stop % FETCHING_BATCH_SIZE) - 1
        elif isinstance(key, int):
            if key < 0:
                key += num_records
            if key < 0 or key >= num_records:
                raise IndexError(f"Index {key} is out of range, dataset has {num_records} records.")
            offsets = [key]
            limits = [1]
        else:
            raise TypeError("Only `int` and `slice` are supported as index.")

        records = []
        for offset, limit in zip(offsets, limits):
            fetched_records = datasets_api_v1.get_records(
                client=self._client,
                id=self._dataset_id,
                offset=offset,
                limit=limit,
                **filters,
            ).parsed
            records.extend([self._parse_record(record) for record in fetched_records.items])
        return records[0] if isinstance(key, int) else records

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def _iter_records(self, filters: Dict[str, Any] = {}) -> Iterator[RemoteFeedbackRecord]:
        """Iterates over the `FeedbackRecord`s of the current `FeedbackDataset` in Argilla."""
        current_batch = 0
        while True:
            batch = datasets_api_v1.get_records(
                client=self._client,
                id=self._dataset_id,
                offset=FETCHING_BATCH_SIZE * current_batch,
                limit=FETCHING_BATCH_SIZE,
                **filters,
            ).parsed
            for record in batch.items:
                yield self._parse_record(record)
            current_batch += 1

            if len(batch.items) < FETCHING_BATCH_SIZE:
                break


class RemoteFeedbackDatasetBase(Generic[T], FeedbackDatasetBase):
    records_cls: Type[T] = None

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
            [record.dict(exclude={"client", "name2id", "id"}, exclude_none=True) for record in self._records]
        )
        return instance
