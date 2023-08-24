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

from argilla.client.feedback.constants import DELETE_DATASET_RECORDS_MAX_NUMBER, PUSHING_BATCH_SIZE
from argilla.client.feedback.dataset.remote.base import RemoteFeedbackDatasetBase, RemoteFeedbackRecordsBase
from argilla.client.feedback.dataset.remote.filtered import FilteredRemoteFeedbackDataset
from argilla.client.feedback.schemas.records import FeedbackRecord, RemoteFeedbackRecord
from argilla.client.sdk.users.models import UserRole
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.sdk.v1.datasets.models import FeedbackResponseStatusFilter
from argilla.client.utils import allowed_for_roles

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes
    from argilla.client.workspaces import Workspace


warnings.simplefilter("always", DeprecationWarning)


class RemoteFeedbackRecords(RemoteFeedbackRecordsBase):
    def __init__(self, dataset: "RemoteFeedbackDataset") -> None:
        super().__init__(dataset=dataset)

    def __getitem__(self, key: Union[slice, int]) -> Union[RemoteFeedbackRecord, List[RemoteFeedbackRecord]]:
        """Returns the record(s) at the given index(es) from Argilla.

        Args:
            key: the index(es) of the record(s) to return. Can either be a single index or a slice.

        Returns:
            Either the record of the given index, or a list with the records at the given indexes.
        """
        return super()._get_records(key=key)

    def __iter__(self) -> Iterator[RemoteFeedbackRecord]:
        """Iterates over the `FeedbackRecord`s of the current `FeedbackDataset` in Argilla."""
        return super()._iter_records()

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
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
            PermissionError: if the user does not have either `owner` or `admin` role.
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
                client=self._client,
                id=self._dataset_id,
                records=records_batch,
            )

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def delete(self, records: List[RemoteFeedbackRecord]) -> None:
        """Deletes a list of `RemoteFeedbackRecord`s from Argilla.

        Args:
            records: A list of `RemoteFeedbackRecord`s to delete from Argilla.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            RuntimeError: If the deletion of the records from Argilla fails.
        """
        num_records = len(records)
        for start in range(0, num_records, DELETE_DATASET_RECORDS_MAX_NUMBER):
            end = min(start + DELETE_DATASET_RECORDS_MAX_NUMBER, num_records)
            try:
                datasets_api_v1.delete_records(
                    client=self._client,
                    id=self._dataset_id,
                    record_ids=[record.id for record in records[start:end]],
                )
            except Exception as e:
                raise RuntimeError("Failed to remove records from Argilla") from e


class RemoteFeedbackDataset(RemoteFeedbackDatasetBase[RemoteFeedbackRecords]):
    records_cls = RemoteFeedbackRecords

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
        super().__init__(
            client=client,
            id=id,
            name=name,
            workspace=workspace,
            fields=fields,
            questions=questions,
            guidelines=guidelines,
        )

    def filter_by(
        self, response_status: Union[FeedbackResponseStatusFilter, List[FeedbackResponseStatusFilter]]
    ) -> FilteredRemoteFeedbackDataset:
        """Filters the current `RemoteFeedbackDataset` based on the `response_status` of
        the responses of the records in Argilla. This method creates a new class instance
        of `FilteredRemoteFeedbackDataset` with the given filters.

        Args:
            response_status: the response status/es to filter the dataset by. Can be
                one of: draft, pending, submitted, and discarded.

        Returns:
            A new instance of `FilteredRemoteFeedbackDataset` with the given filters.
        """
        return FilteredRemoteFeedbackDataset(
            client=self._client,
            id=self.id,
            name=self.name,
            workspace=self.workspace,
            fields=self.fields,
            questions=self.questions,
            guidelines=self.guidelines,
            filters={"response_status": response_status if isinstance(response_status, list) else [response_status]},
        )

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
