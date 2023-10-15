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
from argilla.client.feedback.dataset.mixins import ArgillaMixin, UnificationMixin
from argilla.client.feedback.schemas.enums import RecordSortField, ResponseStatusFilter, SortOrder
from argilla.client.feedback.schemas.metadata import MetadataFilters
from argilla.client.feedback.schemas.types import AllowedQuestionTypes

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.records import FeedbackRecord
    from argilla.client.feedback.schemas.types import (
        AllowedFieldTypes,
        AllowedMetadataPropertyTypes,
        AllowedQuestionTypes,
    )


class FeedbackDataset(FeedbackDatasetBase, ArgillaMixin, UnificationMixin):
    def __init__(
        self,
        *,
        fields: List["AllowedFieldTypes"],
        questions: List["AllowedQuestionTypes"],
        metadata_properties: Optional[List["AllowedMetadataPropertyTypes"]] = None,
        guidelines: Optional[str] = None,
        allow_extra_metadata: bool = True,
    ) -> None:
        """Initializes a `FeedbackDataset` instance locally.

        Args:
            fields: contains the fields that will define the schema of the records in the dataset.
            questions: contains the questions that will be used to annotate the dataset.
            metadata_properties: contains the metadata properties that will be indexed
                and could be used to filter the dataset. Defaults to `None`.
            guidelines: contains the guidelines for annotating the dataset. Defaults to `None`.
            allow_extra_metadata: whether to allow extra metadata that has not been defined
                as a metadata property in the records. Defaults to `True`.

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
            ...     metadata_properties=[
            ...         rg.TermsMetadataProperty(
            ...             name="metadata-property-1",
            ...             values=["a", "b", "c"]
            ...         ),
            ...         rg.IntMetadataProperty(
            ...             name="metadata-property-2",
            ...             gt=0,
            ...             lt=10,
            ...         ),
            ...         rg.FloatMetadataProperty(
            ...             name="metadata-property-2",
            ...             gt=-10.0,
            ...             lt=10.0,
            ...         ),
            ...     ],
            ...     guidelines="These are the annotation guidelines.",
            ... )
        """
        super().__init__(
            fields=fields,
            questions=questions,
            metadata_properties=metadata_properties,
            guidelines=guidelines,
            allow_extra_metadata=allow_extra_metadata,
        )

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

    def sort_by(
        self, field: Union[str, RecordSortField], order: Union[str, SortOrder] = SortOrder.asc
    ) -> "FeedbackDataset":
        warnings.warn(
            "`sort_by` method only works for `FeedbackDataset` pushed to Argilla. "
            "Use `sorted` with dataset.records instead.",
            UserWarning,
            stacklevel=1,
        )
        return self

    def filter_by(
        self,
        *,
        response_status: Optional[Union[ResponseStatusFilter, List[ResponseStatusFilter]]] = None,
        metadata_filters: Optional[Union[MetadataFilters, List[MetadataFilters]]] = None,
    ) -> "FeedbackDataset":
        warnings.warn(
            "`filter_by` method only works for `FeedbackDataset` pushed to Argilla. "
            "Use `filter` with dataset.records instead.",
            UserWarning,
            stacklevel=1,
        )
        return self

    def add_metadata_property(
        self, metadata_property: "AllowedMetadataPropertyTypes"
    ) -> "AllowedMetadataPropertyTypes":
        """Adds the given metadata property to the dataset.

        Args:
            metadata_property: the metadata property to add.

        Returns:
            The metadata property that was added.

        Raises:
            TypeError: if `metadata_property` is not a `MetadataPropertySchema`.
            ValueError: if `metadata_property` is already in the dataset.
        """
        self._unique_metadata_property(metadata_property)
        self._metadata_properties.append(metadata_property)
        return metadata_property

    def delete_metadata_properties(
        self, metadata_properties: Union[str, List[str]]
    ) -> Union["AllowedMetadataPropertyTypes", List["AllowedMetadataPropertyTypes"]]:
        """Deletes the given metadata properties from the dataset.

        Args:
            metadata_properties: the name/s of the metadata property/ies to delete.

        Returns:
            The metadata properties that were deleted.

        Raises:
            TypeError: if `metadata_properties` is not a string or a list of strings.
            ValueError: if the provided `metadata_properties` is/are not in the dataset.
        """
        if not isinstance(metadata_properties, list):
            metadata_properties = [metadata_properties]

        if not self.metadata_properties:
            raise ValueError(
                "The current `FeedbackDataset` does not contain any `metadata_properties` defined, so"
                " none can be deleted."
            )
        metadata_properties_mapping = {
            metadata_property.name: metadata_property for metadata_property in self.metadata_properties
        }
        if not all(
            metadata_property in metadata_properties_mapping.keys() for metadata_property in metadata_properties
        ):
            raise ValueError(
                f"Invalid `metadata_properties={metadata_properties}` provided. It cannot be"
                " deleted because it does not exist, make sure you delete just existing `metadata_properties`"
                " meaning that the name matches any of the existing `metadata_properties` if any. Current"
                f" `metadata_properties` are: '{', '.join(metadata_properties_mapping.keys())}'."
            )

        deleted_metadata_properties = []
        for metadata_property in metadata_properties:
            deleted_metadata_properties.append(metadata_properties_mapping.pop(metadata_property))
        self._metadata_properties = list(metadata_properties_mapping.values())
        return deleted_metadata_properties if len(deleted_metadata_properties) > 1 else deleted_metadata_properties[0]
