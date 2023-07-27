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
from argilla.client.feedback.schemas.records import FeedbackRecord
from argilla.client.sdk.v1.datasets import api as datasets_api_v1

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla.client.feedback.types import AllowedFieldTypes, AllowedQuestionTypes
    from argilla.client.workspaces import Workspace


warnings.simplefilter("always", DeprecationWarning)


class _ArgillaFeedbackDataset(FeedbackDatasetBase):
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
        super().__init__(fields=fields, questions=questions, guidelines=guidelines)

        self.client = client
        self._id = id
        self._name = name
        self._workspace = workspace

        self.__question_id2name = {question.id: question.name for question in self.questions}
        self.__question_name2id = {value: key for key, value in self.__question_id2name.items()}

    @property
    def id(self) -> "UUID":
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def workspace(self) -> "Workspace":
        return self._workspace

    def __len__(self) -> int:
        pass

    def __getitem__(self, key: Union[slice, int]) -> Union[FeedbackRecord, List[FeedbackRecord]]:
        pass

    def __iter__(self) -> Iterator[FeedbackRecord]:
        current_batch = 0
        while True:
            batch = datasets_api_v1.get_records(
                client=self.client,
                id=self.id,
                offset=FETCHING_BATCH_SIZE * current_batch,
                limit=FETCHING_BATCH_SIZE,
            ).parsed
            for record in batch.items:
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
                yield FeedbackRecord(**record)
            current_batch += 1

            if len(batch.items) < FETCHING_BATCH_SIZE:
                break

    def fetch_records(self) -> None:
        pass

    def add_records(
        self,
        records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]],
        show_progress: bool = True,
    ) -> None:
        records = self._validate_records(records)

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
                client=self.client,
                id=self.id,
                records=records_batch,
            )

    def push_to_argilla(self, *args, **kwargs) -> None:
        warnings.warn(
            "`push_to_argilla` is no longer working for a `FeedbackDataset` pushed to Argilla,"
            " as the additions, deletions and/or updates over a `FeedbackDataset` in Argilla"
            " are being tracked automatically, so there's no need to explicitly push them.",
            DeprecationWarning,
        )
