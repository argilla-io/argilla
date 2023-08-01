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

from argilla.client.feedback.constants import FETCHING_BATCH_SIZE
from argilla.client.feedback.dataset.base import FeedbackDatasetBase
from argilla.client.feedback.dataset.mixins import ArgillaToFromMixin
from argilla.client.feedback.types import AllowedFieldTypes, AllowedQuestionTypes

if TYPE_CHECKING:
    from argilla.client.feedback.schemas import FeedbackRecord


warnings.simplefilter("always", DeprecationWarning)


class FeedbackDataset(FeedbackDatasetBase, ArgillaToFromMixin):
    def __init__(
        self,
        *,
        fields: List[AllowedFieldTypes],
        questions: List[AllowedQuestionTypes],
        guidelines: Optional[str] = None,
    ) -> None:
        super().__init__(fields=fields, questions=questions, guidelines=guidelines)

    def __len__(self) -> int:
        """Returns the number of records in the dataset."""
        return len(self.records)

    def __getitem__(self, key: Union[slice, int]) -> Union["FeedbackRecord", List["FeedbackRecord"]]:
        """Returns the record(s) at the given index(es).

        Args:
            key: the index(es) of the record(s) to return. Can either be a single index or a slice.

        Returns:
            Either the record of the given index, or a list with the records at the given indexes.
        """
        if len(self.records) < 1:
            raise RuntimeError(
                "In order to get items from `FeedbackDataset` you need to add them first" " with `add_records`."
            )
        if isinstance(key, int) and len(self.records) < key:
            raise IndexError(f"This dataset contains {len(self)} records, so index {key} is out of range.")
        return self.records[key]

    def iter(self, batch_size: Optional[int] = FETCHING_BATCH_SIZE) -> Iterator[List["FeedbackRecord"]]:
        """Returns an iterator over the records in the dataset.

        Args:
            batch_size: the size of the batches to return. Defaults to 100.
        """
        for i in range(0, len(self.records), batch_size):
            yield self.records[i : i + batch_size]

    def fetch_records(self) -> None:
        warnings.warn(
            "As the current `FeedbackDataset` is stored locally and not pushed to Argilla,"
            " the method `fetch_records` won't do anything. If you want to fetch the records"
            " from Argilla, make sure you're using an `RemoteFeedbackDataset`, either by"
            " calling `FeedbackDataset.from_argilla` or by keeping the returned value from"
            " `FeedbackDataset.push_to_argilla`.",
            DeprecationWarning,
        )

    @property
    def argilla_id(self) -> None:
        warnings.warn(
            "As the current `FeedbackDataset` is stored locally, `argilla_id` won't"
            " return anything as it's not pushed to Argilla. If you want to get the id"
            " of a dataset in Argilla, make sure you're using an `RemoteFeedbackDataset`,"
            " either by calling `FeedbackDataset.from_argilla` or by keeping the returned"
            " value from `FeedbackDataset.push_to_argilla`.",
        )

    def add_records(
        self,
        records: Union["FeedbackRecord", Dict[str, Any], List[Union["FeedbackRecord", Dict[str, Any]]]],
    ) -> None:
        """Adds the given records to the dataset, and stores them locally. If you're planning to add those
        records either to Argilla or HuggingFace, make sure to call `push_to_argilla` or `push_to_huggingface`,
        respectively, after adding the records.

        Args:
            records: the records to add to the dataset. Can be a single record, a list of records or a dictionary
                with the fields of the record.

        Raises:
            ValueError: if the given records are an empty list.
            ValueError: if the given records are neither: `FeedbackRecord`, list of `FeedbackRecord`,
                list of dictionaries as a record or dictionary as a record.
            ValueError: if the given records do not match the expected schema.
        """
        records = self._validate_records(records)

        if len(self.records) > 0:
            self.records += records
        else:
            self.records = records
