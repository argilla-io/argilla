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

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from argilla.client.feedback.dataset.remote.base import RemoteFeedbackDatasetBase, RemoteFeedbackRecordsBase

from argilla.client.sdk.v1.datasets import api as datasets_api_v1

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla.client.feedback.schemas.enums import ResponseStatusFilter
    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from argilla.client.feedback.schemas.records import FeedbackRecord
    from argilla.client.feedback.schemas.remote.records import RemoteFeedbackRecord
    from argilla.client.feedback.schemas.types import AllowedRemoteFieldTypes, AllowedRemoteQuestionTypes
    from argilla.client.sdk.v1.datasets.models import FeedbackRecordsModel
    from argilla.client.workspaces import Workspace


class FilteredRemoteFeedbackRecords(RemoteFeedbackRecordsBase):
    def __init__(self, dataset: "RemoteFeedbackDataset", filters: Dict[str, Any]) -> None:
        super().__init__(dataset=dataset)

        self._filters = filters

    def __len__(self) -> None:
        raise NotImplementedError("`__len__` does not work for filtered datasets.")

    def _fetch_records(self, offset: int, limit: int) -> "FeedbackRecordsModel":
        """Fetches a batch of records from Argilla."""
        return datasets_api_v1.get_records(
            client=self._client,
            id=self._dataset.id,
            offset=offset,
            limit=limit,
            **self._filters,
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
        filters: Dict[str, Any] = {},
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
            filters=filters,
        )

    def delete(self) -> None:
        raise NotImplementedError("`delete` does not work for filtered datasets.")

    def filter_by(
        self, response_status: Union["ResponseStatusFilter", List["ResponseStatusFilter"]]
    ) -> "FilteredRemoteFeedbackDataset":
        if not isinstance(response_status, list):
            response_status = [response_status]

        return self.__class__(
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
