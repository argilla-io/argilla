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
from argilla.client.feedback.schemas.records import FeedbackRecord, _ArgillaFeedbackRecord
from argilla.client.sdk.v1.datasets import api as datasets_api_v1

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla.client.feedback.types import AllowedFieldTypes, AllowedQuestionTypes
    from argilla.client.sdk.v1.datasets.models import FeedbackItemModel
    from argilla.client.workspaces import Workspace


warnings.simplefilter("always", DeprecationWarning)


class _ArgillaFeedbackRecords:
    def __init__(self, client: "httpx.Client", id: "UUID", questions: List["AllowedQuestionTypes"]) -> None:
        self.client = client
        self.id = id

        self.__question_id2name = {question.id: question.name for question in questions}
        self.__question_name2id = {value: key for key, value in self.__question_id2name.items()}

    def __repr__(self) -> str:
        return (
            "The `records` of a `FeedbackDataset` in Argilla are being lazily"
            " fetched, and never stored locally. You can either loop over `records`"
            " or access them by index, and those will be fetched from Argilla on the"
            " fly."
        )

    def __parse_record(self, record: "FeedbackItemModel") -> _ArgillaFeedbackRecord:
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
        return _ArgillaFeedbackRecord(client=self.client, name2id=self.__question_name2id, **record)

    def __len__(self) -> int:
        try:
            response = datasets_api_v1.get_metrics(client=self.client, id=self.id)
        except Exception as e:
            raise Exception(
                f"Failed while getting the metrics from the current `FeedbackDataset` in Argilla with exception: {e}"
            ) from e
        return response.parsed.records.count

    def __getitem__(self, key: Union[slice, int]) -> Union[_ArgillaFeedbackRecord, List[_ArgillaFeedbackRecord]]:
        offsets = []
        limit = None
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            if step is not None and step != 1:
                return [self[i] for i in range(start, stop, step)]
            if start < 0:
                start += len(self)
            if stop < 0:
                stop += len(self)
            if start < 0 or stop < 0:
                raise IndexError("Index out of range")
            limit = stop - start
            offsets = [start] if limit < FETCHING_BATCH_SIZE else list(range(start, stop, FETCHING_BATCH_SIZE))
        elif isinstance(key, int):
            if key < 0:
                key += len(self)
            if key < 0 or key >= len(self):
                raise IndexError("Index out of range")
            offsets = [key]
            limit = 1
        else:
            raise TypeError("Invalid argument type")

        records = []
        for offset in offsets:
            fetched_records = datasets_api_v1.get_records(
                client=self.client,
                id=self.id,
                offset=offset,
                limit=limit,
            ).parsed
            if len(fetched_records.items) == 1:
                record = fetched_records.items[0]
                records.append(self.__parse_record(record))
            else:
                records.extend([self.__parse_record(record) for record in fetched_records.items])
        return records[0] if isinstance(key, int) else records

    def __iter__(self) -> Iterator[_ArgillaFeedbackRecord]:
        current_batch = 0
        while True:
            batch = datasets_api_v1.get_records(
                client=self.client,
                id=self.id,
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
        records: Union[FeedbackRecord, List[FeedbackRecord]],
        show_progress: bool = True,
    ) -> None:
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

        self.records: _ArgillaFeedbackRecords = _ArgillaFeedbackRecords(
            client=self.client, id=self.id, questions=self.questions
        )

    @property
    def argilla_id(self) -> str:
        warnings.warn(
            "`argilla_id` is deprected in favor of `id` and will be removed in a future"
            " release. Please use `id` instead.",
            DeprecationWarning,
        )
        return self.id

    @property
    def id(self) -> "UUID":
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def workspace(self) -> "Workspace":
        return self._workspace

    def __repr__(self) -> str:
        return f"<ArgillaFeedbackDataset id={self.id} name={self.name} workspace={self.workspace}>"

    def __len__(self) -> int:
        return self.records.__len__()

    def __iter__(self) -> Iterator[_ArgillaFeedbackRecord]:
        return self.records.__iter__()

    def __getitem__(self, key: Union[slice, int]) -> Union[_ArgillaFeedbackRecord, List[_ArgillaFeedbackRecord]]:
        return self.records.__getitem__(key)

    def fetch_records(self) -> List[_ArgillaFeedbackRecord]:
        raise NotImplementedError("This method is not implemented yet")

    def push_to_argilla(self, *args, **kwargs) -> None:
        warnings.warn(
            "`push_to_argilla` is no longer working for a `FeedbackDataset` pushed to Argilla,"
            " as the additions, deletions and/or updates over a `FeedbackDataset` in Argilla"
            " are being tracked automatically, so there's no need to explicitly push them.",
            DeprecationWarning,
        )

    def add_records(
        self,
        records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]],
        show_progress: bool = True,
    ) -> None:
        records = self._validate_records(records=records)
        self.records.add(records=records, show_progress=show_progress)
