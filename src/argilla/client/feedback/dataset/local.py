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
        """Initializes a `FeedbackDataset` instance locally.

        Args:
            fields: contains the fields that will define the schema of the records in the dataset.
            questions: contains the questions that will be used to annotate the dataset.
            guidelines: contains the guidelines for annotating the dataset. Defaults to `None`.

        Raises:
            TypeError: if `fields` is not a list of `FieldSchema`.
            ValueError: if `fields` does not contain at least one required field.
            TypeError: if `questions` is not a list of `TextQuestion`, `RatingQuestion`,
                `LabelQuestion`, and/or `MultiLabelQuestion`.
            ValueError: if `questions` does not contain at least one required question.
            TypeError: if `guidelines` is not None and not a string.
            ValueError: if `guidelines` is an empty string.

        Examples:
            >>> import argilla as rg
            >>> rg.init(api_url="...", api_key="...")
            >>> dataset = rg.FeedbackDataset(
            ...     fields=[
            ...         rg.TextField(name="text", required=True),
            ...         rg.TextField(name="label", required=True),
            ...     ],
            ...     questions=[
            ...         rg.TextQuestion(
            ...             name="question-1",
            ...             description="This is the first question",
            ...             required=True,
            ...         ),
            ...         rg.RatingQuestion(
            ...             name="question-2",
            ...             description="This is the second question",
            ...             required=True,
            ...             values=[1, 2, 3, 4, 5],
            ...         ),
            ...         rg.LabelQuestion(
            ...             name="question-3",
            ...             description="This is the third question",
            ...             required=True,
            ...             labels=["positive", "negative"],
            ...         ),
            ...         rg.MultiLabelQuestion(
            ...             name="question-4",
            ...             description="This is the fourth question",
            ...             required=True,
            ...             labels=["category-1", "category-2", "category-3"],
            ...         ),
            ...     ],
            ...     guidelines="These are the annotation guidelines.",
            ... )
        """
        super().__init__(fields=fields, questions=questions, guidelines=guidelines)

        self._records = []

    @property
    def records(self) -> List["FeedbackRecord"]:
        """Returns the records in the dataset."""
        return self._records

    def __repr__(self) -> str:
        """Returns a string representation of the dataset."""
        return f"<FeedbackDataset fields={self.fields} questions={self.questions} guidelines={self.guidelines}>"

    def __len__(self) -> int:
        """Returns the number of records in the dataset."""
        return len(self._records)

    def __getitem__(self, key: Union[slice, int]) -> Union["FeedbackRecord", List["FeedbackRecord"]]:
        """Returns the record(s) at the given index(es).

        Args:
            key: the index(es) of the record(s) to return. Can either be a single index or a slice.

        Returns:
            Either the record of the given index, or a list with the records at the given indexes.
        """
        if len(self._records) < 1:
            raise RuntimeError(
                "In order to get items from `FeedbackDataset` you need to add them first" " with `add_records`."
            )
        if isinstance(key, int) and len(self._records) < key:
            raise IndexError(f"This dataset contains {len(self)} records, so index {key} is out of range.")
        return self._records[key]

    def iter(self, batch_size: Optional[int] = FETCHING_BATCH_SIZE) -> Iterator[List["FeedbackRecord"]]:
        """Returns an iterator over the records in the dataset.

        Args:
            batch_size: the size of the batches to return. Defaults to 100.
        """
        for i in range(0, len(self._records), batch_size):
            yield self._records[i : i + batch_size]

    def fetch_records(self) -> None:
        warnings.warn(
            "As the current `FeedbackDataset` is stored locally and not pushed to Argilla,"
            " the method `fetch_records` won't do anything. If you want to fetch the records"
            " from Argilla, make sure you're using an `RemoteFeedbackDataset`, either by"
            " calling `FeedbackDataset.from_argilla` or by keeping the returned value from"
            " `FeedbackDataset.push_to_argilla`.\n`fetch_records` will be deprecated in"
            " Argilla v1.15.0.",
            DeprecationWarning,
            stacklevel=1,
        )

    @property
    def argilla_id(self) -> None:
        warnings.warn(
            "As the current `FeedbackDataset` is stored locally, `argilla_id` won't"
            " return anything as it's not pushed to Argilla. If you want to get the id"
            " of a dataset in Argilla, make sure you're using an `RemoteFeedbackDataset`,"
            " either by calling `FeedbackDataset.from_argilla` or by keeping the returned"
            " value from `FeedbackDataset.push_to_argilla`.\n`argilla_id` will be deprecated in"
            " Argilla v1.15.0.",
            DeprecationWarning,
            stacklevel=1,
        )

    def add_records(
        self,
        records: Union["FeedbackRecord", Dict[str, Any], List[Union["FeedbackRecord", Dict[str, Any]]]],
    ) -> None:
        """Adds the given records to the dataset, and stores them locally. If you are
        planning to push those to Argilla, you will need to call `push_to_argilla` afterwards,
        to both create the dataset in Argilla and push the records to it. Then, from a
        `FeedbackDataset` pushed to Argilla, you'll just need to call `add_records` and
        those will be automatically uploaded to Argilla.

        Args:
            records: can be a single `FeedbackRecord`, a list of `FeedbackRecord`,
                a single dictionary, or a list of dictionaries. If a dictionary is provided,
                it will be converted to a `FeedbackRecord` internally.

        Raises:
            ValueError: if the given records are an empty list.
            ValueError: if the given records are neither: `FeedbackRecord`, list of `FeedbackRecord`,
                list of dictionaries as a record or dictionary as a record.
            ValueError: if the given records do not match the expected schema.
        """
        records = self._parse_records(records)
        self._validate_records(records)

        if len(self._records) > 0:
            self._records += records
        else:
            self._records = records
