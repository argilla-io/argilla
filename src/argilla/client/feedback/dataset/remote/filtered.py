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

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from argilla.client.feedback.dataset.remote.base import RemoteFeedbackDatasetBase, RemoteFeedbackRecordsBase

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from argilla.client.feedback.schemas.records import FeedbackRecord, RemoteFeedbackRecord
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes
    from argilla.client.workspaces import Workspace


class FilteredRemoteFeedbackRecords(RemoteFeedbackRecordsBase):
    def __init__(self, dataset: "RemoteFeedbackDataset", filters: Dict[str, Any]) -> None:
        super().__init__(dataset=dataset)

        self._filters = filters

    def __len__(self) -> None:
        raise NotImplementedError("`records.__len__` does not work for filtered datasets.")

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
        fields: List["AllowedFieldTypes"],
        questions: List["AllowedQuestionTypes"],
        guidelines: Optional[str] = None,
        filters: Dict[str, Any] = {},
    ) -> None:
        super().__init__(
            client=client,
            id=id,
            name=name,
            workspace=workspace,
            fields=fields,
            questions=questions,
            guidelines=guidelines,
            # kwargs
            filters=filters,
        )

    def add_records(
        self,
        records: Union["FeedbackRecord", Dict[str, Any], List[Union["FeedbackRecord", Dict[str, Any]]]],
        show_progress: bool = True,
    ) -> None:
        raise NotImplementedError("`add_records` does not work for filtered datasets.")

    def delete_records(self, records: Union["RemoteFeedbackRecord", List["RemoteFeedbackRecord"]]) -> None:
        raise NotImplementedError("`delete_records` does not work for filtered datasets.")

    def delete(self) -> None:
        raise NotImplementedError("`delete` does not work for filtered datasets.")
