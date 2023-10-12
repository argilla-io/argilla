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
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from tqdm import trange

from argilla.client.feedback.constants import DELETE_DATASET_RECORDS_MAX_NUMBER, PUSHING_BATCH_SIZE
from argilla.client.feedback.dataset.remote.base import RemoteFeedbackDatasetBase, RemoteFeedbackRecordsBase
from argilla.client.feedback.dataset.remote.filtered import FilteredRemoteFeedbackDataset
from argilla.client.feedback.schemas.records import FeedbackRecord
from argilla.client.feedback.schemas.remote.records import RemoteFeedbackRecord
from argilla.client.feedback.training.schemas import (
    TrainingTaskTypes,
)
from argilla.client.models import Framework
from argilla.client.sdk.users.models import UserRole
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.utils import allowed_for_roles

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla.client.feedback.schemas.enums import ResponseStatusFilter
    from argilla.client.feedback.schemas.types import AllowedRemoteFieldTypes, AllowedRemoteQuestionTypes
    from argilla.client.sdk.v1.datasets.models import FeedbackRecordsModel
    from argilla.client.workspaces import Workspace


class RemoteFeedbackRecords(RemoteFeedbackRecordsBase):
    def __init__(self, dataset: "RemoteFeedbackDataset") -> None:
        super().__init__(dataset=dataset)

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def __len__(self) -> int:
        """Returns the number of records in the current `FeedbackDataset` in Argilla."""
        try:
            response = datasets_api_v1.get_metrics(client=self._client, id=self._dataset.id)
        except Exception as e:
            raise Exception(
                f"Failed while getting the metrics from the current `FeedbackDataset` in Argilla with exception: {e}"
            ) from e
        return response.parsed.records.count

    def _fetch_records(self, offset: int, limit: int) -> "FeedbackRecordsModel":
        """Fetches a batch of records from Argilla."""
        return datasets_api_v1.get_records(
            client=self._client,
            id=self._dataset.id,
            offset=offset,
            limit=limit,
        ).parsed

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
            datasets_api_v1.add_records(
                client=self._client,
                id=self._dataset.id,
                records=[
                    record.to_server_payload(self._question_name_to_id)
                    for record in records[i : i + PUSHING_BATCH_SIZE]
                ],
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
                    id=self._dataset.id,
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
        created_at: datetime,
        updated_at: datetime,
        fields: List["AllowedRemoteFieldTypes"],
        questions: List["AllowedRemoteQuestionTypes"],
        guidelines: Optional[str] = None,
    ) -> None:
        super().__init__(
            client=client,
            id=id,
            name=name,
            workspace=workspace,
            created_at=created_at,
            updated_at=updated_at,
            fields=fields,
            questions=questions,
            guidelines=guidelines,
        )

    def filter_by(
        self, response_status: Union["ResponseStatusFilter", List["ResponseStatusFilter"]]
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
        if not isinstance(response_status, list):
            response_status = [response_status]
        return FilteredRemoteFeedbackDataset(
            client=self._client,
            id=self.id,
            name=self.name,
            workspace=self.workspace,
            created_at=self.created_at,
            updated_at=self.updated_at,
            fields=self.fields,
            questions=self.questions,
            guidelines=self.guidelines,
            filters={
                "response_status": [status.value if hasattr(status, "value") else status for status in response_status]
            },
        )

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

    def unify_responses(self, *args, **kwargs) -> "FeedbackDataset":
        warnings.warn(
            "A local `FeedbackDataset` returned because"
            "`unify_responses` is not supported for `RemoteFeedbackDataset`. "
            "`RemoteFeedbackDataset`.pull().unify_responses(*args, **kwargs)` is applied.",
            UserWarning,
        )
        local = self.pull()
        return local.unify_responses(*args, **kwargs)

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
        warnings.warn(
            (
                "A local `FeedbackDataset` returned because"
                "`prepare_for_training` is not supported for `RemoteFeedbackDataset`. "
                "`RemoteFeedbackDataset`.pull().prepare_for_training(*args, **kwargs)` is applied."
            ),
            UserWarning,
        )
        local = self.pull()
        return local.prepare_for_training(
            framework=framework,
            task=task,
            train_size=train_size,
            test_size=test_size,
            seed=seed,
            lang=lang,
        )
