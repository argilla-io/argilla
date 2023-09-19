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

from typing import TYPE_CHECKING, Iterator, List, Union

from argilla.client.feedback.constants import FETCHING_BATCH_SIZE
from argilla.client.feedback.schemas.remote.records import RemoteFeedbackRecord
from argilla.client.sdk.users.models import UserRole
from argilla.client.utils import allowed_for_roles

if TYPE_CHECKING:
    from argilla.client.feedback.dataset.remote.base import RemoteFeedbackRecordsBase


class ArgillaRecordsMixin:
    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def __getitem__(
        self: "RemoteFeedbackRecordsBase", key: Union[slice, int]
    ) -> Union["RemoteFeedbackRecord", List["RemoteFeedbackRecord"]]:
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
            fetched_records = self._fetch_records(offset=offset, limit=limit)
            records.extend(
                [
                    RemoteFeedbackRecord.from_api(record, question_id_to_name=self._question_id_to_name)
                    for record in fetched_records.items
                ]
            )
        return records[0] if isinstance(key, int) else records

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def __iter__(
        self: "RemoteFeedbackRecordsBase",
    ) -> Iterator["RemoteFeedbackRecord"]:
        """Iterates over the `FeedbackRecord`s of the current `FeedbackDataset` in Argilla."""
        current_batch = 0
        while True:
            batch = self._fetch_records(offset=FETCHING_BATCH_SIZE * current_batch, limit=FETCHING_BATCH_SIZE)
            for record in batch.items:
                yield RemoteFeedbackRecord.from_api(record, question_id_to_name=self._question_id_to_name)
            current_batch += 1

            if len(batch.items) < FETCHING_BATCH_SIZE:
                break
