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

from argilla.client.feedback.dataset.remote.base import RemoteFeedbackDatasetBase, RemoteFeedbackRecordsBase
from argilla.client.feedback.schemas.metadata import MetadataFilters
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.sdk.v1.datasets.models import FeedbackRecordsModel, FeedbackResponseStatusFilter

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from argilla.client.feedback.schemas.records import FeedbackRecord
    from argilla.client.feedback.schemas.remote.records import RemoteFeedbackRecord
    from argilla.client.feedback.schemas.types import AllowedRemoteFieldTypes, AllowedRemoteQuestionTypes
    from argilla.client.workspaces import Workspace


class FilteredRemoteFeedbackRecords(RemoteFeedbackRecordsBase):
    def __init__(
        self,
        dataset: "RemoteFeedbackDataset",
        response_status: Optional[List["FeedbackResponseStatusFilter"]] = None,
        metadata_filters: Optional[List["MetadataFilters"]] = None,
    ) -> None:
        super().__init__(dataset=dataset)

        self._response_status = (
            [
                status.value if hasattr(status, "value") else FeedbackResponseStatusFilter(status).value
                for status in response_status
            ]
            if response_status
            else None
        )
        self._metadata_filters = (
            [metadata_filter.query_string for metadata_filter in metadata_filters] if metadata_filters else None
        )

    def __len__(self) -> None:
        warnings.warn(
            "The `records` of a filtered dataset in Argilla are being lazily loaded"
            " and len computation may add undesirable extra computation. You can fetch"
            "records using\n`ds.pull()`\nor iterate over results to know the length of the result:\n"
            "`records = [r for r in ds.records]\n",
            stacklevel=1,
        )

    def _fetch_records(self, offset: int, limit: int) -> "FeedbackRecordsModel":
        """Fetches a batch of records from Argilla."""
        return datasets_api_v1.get_records(
            client=self._client,
            id=self._dataset.id,
            offset=offset,
            limit=limit,
            response_status=self._response_status,
            metadata_filters=self._metadata_filters,
        ).parsed

    def add(
        self,
        records: Union["FeedbackRecord", Dict[str, Any], List[Union["FeedbackRecord", Dict[str, Any]]]],
        show_progress: bool = True,
    ) -> None:
        raise NotImplementedError("`records.add` does not work for filtered datasets.")

    def delete(self, records: List["RemoteFeedbackRecord"]) -> None:
        raise NotImplementedError("`records.delete` does not work for filtered datasets.")


class FilteredRemoteFeedbackDataset(RemoteFeedbackDatasetBase[FilteredRemoteFeedbackRecords]):
    records_cls = FilteredRemoteFeedbackRecords

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
        response_status: Optional[List["FeedbackResponseStatusFilter"]] = None,
        metadata_filters: Optional[List["MetadataFilters"]] = None,
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
            # kwargs
            response_status=response_status,
            metadata_filters=metadata_filters,
        )

    def delete(self) -> None:
        raise NotImplementedError("`delete` does not work for filtered datasets.")
