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

from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Union

from argilla.client.feedback.dataset.remote.base import RemoteFeedbackDatasetBase, RemoteFeedbackRecordsBase
from argilla.client.feedback.schemas.records import RemoteFeedbackRecord

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
    from argilla.client.feedback.schemas.records import FeedbackRecord
    from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes
    from argilla.client.workspaces import Workspace


class FilteredRemoteFeedbackRecords(RemoteFeedbackRecordsBase):
    def __init__(self, dataset: "RemoteFeedbackDataset", filters: Dict[str, Any]) -> None:
        super().__init__(dataset=dataset)

        self._filters = filters

    def __getitem__(self, key: Union[slice, int]) -> Union[RemoteFeedbackRecord, List[RemoteFeedbackRecord]]:
        """Returns the record(s) at the given index(es) from Argilla.

        Args:
            key: the index(es) of the record(s) to return. Can either be a single index or a slice.

        Returns:
            Either the record of the given index, or a list with the records at the given indexes.
        """
        return super()._get_records(key=key, filters=self._filters)

    def __iter__(self) -> Iterator[RemoteFeedbackRecord]:
        """Iterates over the `FeedbackRecord`s of the current `FeedbackDataset` in Argilla."""
        return super()._iter_records(filters=self._filters)


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
