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
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Union

from tqdm import trange

from argilla.client.feedback.constants import FETCHING_BATCH_SIZE, PUSHING_BATCH_SIZE
from argilla.client.feedback.dataset.base import FeedbackDatasetBase
from argilla.client.feedback.schemas.records import FeedbackRecord, RemoteFeedbackRecord
from argilla.client.sdk.users.models import UserRole
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.sdk.v1.records import api as records_api_v1
from argilla.client.utils import allowed_for_roles

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla.client.feedback.dataset.local import FeedbackDataset
    from argilla.client.feedback.types import AllowedFieldTypes, AllowedQuestionTypes
    from argilla.client.sdk.v1.datasets.models import FeedbackItemModel
    from argilla.client.workspaces import Workspace


warnings.simplefilter("always", DeprecationWarning)


class RemoteFeedbackRecords:
    def __init__(self, dataset: "RemoteFeedbackDataset") -> None:
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
        self.__question_id2name = {question.id: question.name for question in self._dataset.questions}
        self.__question_name2id = {value: key for key, value in self.__question_id2name.items()}

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

    def __parse_record(self, record: "FeedbackItemModel") -> RemoteFeedbackRecord:
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
        return RemoteFeedbackRecord(client=self._dataset._client, name2id=self.__question_name2id, **record)

    def __len__(self) -> int:
        """Returns the number of records in the current `FeedbackDataset` in Argilla."""
        try:
            response = datasets_api_v1.get_metrics(client=self._dataset._client, id=self._dataset._id)
        except Exception as e:
            raise Exception(
                f"Failed while getting the metrics from the current `FeedbackDataset` in Argilla with exception: {e}"
            ) from e
        return response.parsed.records.count

    def __getitem__(self, key: Union[slice, int]) -> Union[RemoteFeedbackRecord, List[RemoteFeedbackRecord]]:
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
                client=self._dataset._client,
                id=self._dataset._id,
                offset=offset,
                limit=limit,
            ).parsed
            records.extend([self.__parse_record(record) for record in fetched_records.items])
        return records[0] if isinstance(key, int) else records

    def __iter__(self) -> Iterator[RemoteFeedbackRecord]:
        """Iterates over the `FeedbackRecord`s of the current `FeedbackDataset` in Argilla."""
        current_batch = 0
        while True:
            batch = datasets_api_v1.get_records(
                client=self._dataset._client,
                id=self._dataset._id,
                offset=FETCHING_BATCH_SIZE * current_batch,
                limit=FETCHING_BATCH_SIZE,
            ).parsed
            for record in batch.items:
                yield self.__parse_record(record)
            current_batch += 1

            if len(batch.items) < FETCHING_BATCH_SIZE:
                break

    def add(
        self,
        records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]],
        show_progress: bool = True,
    ) -> None:
        """Pushes a list of `FeedbackRecord`s to Argilla.

        Args:
            records: can be a single `FeedbackRecord`, a list of `FeedbackRecord`,
                a single dictionary, or a list of dictionaries. If a dictionary is provided,
                it will be converted to a `FeedbackRecord` internally.
            show_progress: Whether to show a `tqdm` progress bar while pushing the records.

        Raises:
            Exception: If the pushing of the records to Argilla fails.
        """
        records = self._dataset._parse_and_validate_records(records)
        for i in trange(
            0, len(records), PUSHING_BATCH_SIZE, desc="Pushing records to Argilla...", disable=not show_progress
        ):
            records_batch = []
            for record in records[i : i + PUSHING_BATCH_SIZE]:
                if record.suggestions:
                    for suggestion in record.suggestions:
                        suggestion.question_id = self.__question_name2id[suggestion.question_name]
                records_batch.append(
                    record.dict(exclude={"id": ..., "suggestions": {"__all__": {"question_name"}}}, exclude_none=True)
                )
            datasets_api_v1.add_records(
                client=self._dataset._client,
                id=self._dataset._id,
                records=records_batch,
            )

    def delete(
        self,
        records: List[RemoteFeedbackRecord],
    ) -> None:
        """Deletes a list of `RemoteFeedbackRecord`s from Argilla.

        Args:
            records: A list of `RemoteFeedbackRecord`s to delete from Argilla.

        Raises:
            RuntimeError: If the deletion of the records from Argilla fails.
        """
        for record in records:
            try:
                records_api_v1.delete_record(client=self._dataset._client, id=record.id)
            except Exception as e:
                raise RuntimeError(f"Failed to delete record with id {record.id} from Argilla.") from e


class RemoteFeedbackDataset(FeedbackDatasetBase):
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

        self._client = client
        self._id = id
        self._name = name
        self._workspace = workspace

        self._records: RemoteFeedbackRecords = RemoteFeedbackRecords(dataset=self)

    @property
    def records(self) -> RemoteFeedbackRecords:
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

    def add_records(
        self,
        records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]],
        show_progress: bool = True,
    ) -> None:
        """Adds the given records to the dataset and pushes those to Argilla.

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
        self._records.add(records=records, show_progress=show_progress)

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def delete_records(self, records: Union["RemoteFeedbackRecord", List["RemoteFeedbackRecord"]]) -> None:
        """Deletes the given records from the dataset in Argilla.

        Args:
            records: the records to delete from the dataset. Can be a single record or a list
                of records. But those need to be previously pushed to Argilla, otherwise
                they won't be deleted.

        Raises:
            RuntimeError: If the deletion of the records from Argilla fails.
        """
        self._records.delete(records=[records] if not isinstance(records, list) else records)

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def delete(self) -> None:
        """Deletes the current `FeedbackDataset` from Argilla. This method is just working
        if the user has either `owner` or `admin` role.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            RuntimeError: if the `FeedbackDataset` cannot be deleted from Argilla.
        """
        try:
            datasets_api_v1.delete_dataset(client=self._client, id=self.id)
        except Exception as e:
            raise RuntimeError(f"Failed while deleting the `FeedbackDataset` from Argilla with exception: {e}") from e
