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

import textwrap
import warnings
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Literal, Optional, Tuple, Union

from rich.progress import Progress

from argilla_v1.client.feedback.constants import DELETE_DATASET_RECORDS_MAX_NUMBER, PUSHING_BATCH_SIZE
from argilla_v1.client.feedback.dataset import helpers
from argilla_v1.client.feedback.dataset.base import FeedbackDatasetBase, SortBy
from argilla_v1.client.feedback.dataset.mixins import MetricsMixin, UnificationMixin
from argilla_v1.client.feedback.dataset.remote.mixins import ArgillaRecordsMixin
from argilla_v1.client.feedback.mixins import ArgillaMetadataPropertiesMixin
from argilla_v1.client.feedback.schemas.enums import ResponseStatusFilter
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.feedback.schemas.remote.records import RemoteFeedbackRecord
from argilla_v1.client.feedback.schemas.remote.vector_settings import RemoteVectorSettings
from argilla_v1.client.feedback.schemas.vector_settings import VectorSettings
from argilla_v1.client.feedback.training.schemas.base import (
    TrainingTaskTypes,
)
from argilla_v1.client.models import Framework
from argilla_v1.client.sdk.commons.errors import AlreadyExistsApiError
from argilla_v1.client.sdk.users.models import UserRole
from argilla_v1.client.sdk.v1.datasets import api as datasets_api_v1
from argilla_v1.client.sdk.v1.datasets.models import FeedbackRecordsSearchVectorQuery
from argilla_v1.client.sdk.v1.vectors_settings import api as vectors_settings_api_v1
from argilla_v1.client.utils import allowed_for_roles

INCLUDE_ALL_VECTORS_PARAM: str = "all"

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
    from argilla_v1.client.feedback.schemas.metadata import MetadataFilters
    from argilla_v1.client.feedback.schemas.types import (
        AllowedMetadataPropertyTypes,
        AllowedRemoteFieldTypes,
        AllowedRemoteMetadataPropertyTypes,
        AllowedRemoteQuestionTypes,
    )
    from argilla_v1.client.sdk.v1.datasets.models import FeedbackRecordsModel
    from argilla_v1.client.workspaces import Workspace


class RemoteFeedbackRecords(ArgillaRecordsMixin):
    def __init__(
        self,
        dataset: "RemoteFeedbackDataset",
        response_status: Optional[Union[ResponseStatusFilter, List[ResponseStatusFilter]]] = None,
        metadata_filters: Optional[Union["MetadataFilters", List["MetadataFilters"]]] = None,
        sort_by: Optional[List[SortBy]] = None,
        with_vectors: Union[INCLUDE_ALL_VECTORS_PARAM, List[str], None] = None,
    ) -> None:
        """Initializes a `RemoteFeedbackRecords` instance to access a `FeedbackDataset`
        records in Argilla. This class is used to get records from Argilla, iterate over
        them, and push new records to Argilla.

        Note:
            This class is not intended to be initialised directly. Instead, use
            `FeedbackDataset.from_argilla` to get an instance of `RemoteFeedbackDataset`,
            and then just call `records` on it.

        Args:
            dataset: the `RemoteFeedbackDataset` instance to access the `httpx.Client`,
                the ID of the dataset in Argilla, and everything else to reuse some methods
                and/or attributes.
        """
        self._dataset = dataset

        if response_status and not isinstance(response_status, list):
            response_status = [response_status]
        if metadata_filters and not isinstance(metadata_filters, list):
            metadata_filters = [metadata_filters]

        # TODO: Validate filters and sort exists in metadata
        self._sort_by = sort_by or []
        self._response_status = response_status or []
        self._metadata_filters = metadata_filters or []

        self._with_vectors = with_vectors

        self._validate_metadata_names()
        self._validate_vector_names()

    @property
    def dataset(self) -> "RemoteFeedbackDataset":
        """Returns the `RemoteFeedbackDataset` instance that this `RemoteFeedbackRecords` belongs to."""
        return self._dataset

    @property
    def sort_by(self) -> Optional[List[SortBy]]:
        """Returns the sort by fields and orders that this `RemoteFeedbackRecords` is using."""
        return [sort_by for sort_by in self._sort_by]

    @property
    def metadata_filters(self) -> Optional[List["MetadataFilters"]]:
        """Returns the metadata filters that this `RemoteFeedbackRecords` is using."""
        return [metadata_filter for metadata_filter in self._metadata_filters]

    @property
    def response_status(self) -> Optional[List[ResponseStatusFilter]]:
        """Returns the response status filters that this `RemoteFeedbackRecords` is using."""
        return [ResponseStatusFilter(response_status) for response_status in self._response_status]

    @property
    def _client(self) -> "httpx.Client":
        """Returns the `httpx.Client` instance that will be used to send requests to Argilla."""
        return self.dataset._client

    @property
    def _question_id_to_name(self) -> Dict["UUID", str]:
        return self.dataset._question_id_to_name

    @property
    def _question_name_to_id(self) -> Dict[str, "UUID"]:
        return self.dataset._question_name_to_id

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def __len__(self) -> int:
        """Returns the number of records in the current `FeedbackDataset` in Argilla."""
        try:
            if self._has_filters():
                return self._fetch_records(offset=0, limit=1).total
            else:
                response = datasets_api_v1.get_metrics(client=self._client, id=self._dataset.id).parsed
                return response.records.count
        except Exception as e:
            raise Exception(
                f"Failed while getting the metrics from the current `FeedbackDataset` in Argilla with exception: {e}"
            ) from e

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def add(
        self,
        records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]],
        show_progress: bool = True,
    ) -> None:
        """Pushes a list of `FeedbackRecord`s to Argilla.

        Args:
            records: can be a single `FeedbackRecord`, a list of `FeedbackRecord`,
                a single dictionary, or a list of dictionaries. If a dictionary is provided,
                it will be converted to a `FeedbackRecord` internally.
            show_progress: Whether to show a `tqdm` progress bar while pushing the records.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            Exception: If the pushing of the records to Argilla fails.
        """
        records = helpers.normalize_records(records)
        helpers.validate_dataset_records(self.dataset, records)

        question_name_to_id = {question.name: question.id for question in self.dataset.questions}

        with Progress() as progress_bar:
            task = progress_bar.add_task("Pushing records to Argilla...", total=len(records), visible=show_progress)

            for i in range(0, len(records), PUSHING_BATCH_SIZE):
                batch = records[i : i + PUSHING_BATCH_SIZE]
                datasets_api_v1.add_records(
                    client=self._client,
                    id=self.dataset.id,
                    records=[record.to_server_payload(question_name_to_id=question_name_to_id) for record in batch],
                )
                progress_bar.update(task, advance=len(batch))

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def update(
        self,
        records: Union[RemoteFeedbackRecord, List[RemoteFeedbackRecord]],
        show_progress: bool = True,
    ) -> None:
        """Updates a list of `RemoteFeedbackRecord`s in Argilla.

        Args:
            records: can be a single `RemoteFeedbackRecord` or a list of
                `RemoteFeedbackRecord`.
            show_progress: Whether to show a `tqdm` progress bar while updating the records.
        """
        if isinstance(records, RemoteFeedbackRecord):
            records = [records]

        helpers.validate_dataset_records(self.dataset, records, attributes_to_validate=["metadata", "vectors"])

        with Progress() as progress_bar:
            task = progress_bar.add_task("Updating records in Argilla...", total=len(records), visible=show_progress)

            for i in range(0, len(records), PUSHING_BATCH_SIZE):
                batch = records[i : i + PUSHING_BATCH_SIZE]
                datasets_api_v1.update_records(
                    client=self._client,
                    id=self.dataset.id,
                    records=[
                        {"id": str(record.id), **record.to_server_payload(self._question_name_to_id)}
                        for record in batch
                    ],
                )
                progress_bar.update(task, advance=len(batch))

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def delete(self, records: List[RemoteFeedbackRecord]) -> None:
        """Deletes a list of `RemoteFeedbackRecord`s from Argilla.

        Args:
            records: A list of `RemoteFeedbackRecord`s to delete from Argilla.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            RuntimeError: If the deletion of the records from Argilla fails.
        """
        num_records = len(records)
        for start in range(0, num_records, DELETE_DATASET_RECORDS_MAX_NUMBER):
            end = min(start + DELETE_DATASET_RECORDS_MAX_NUMBER, num_records)
            try:
                datasets_api_v1.delete_records(
                    client=self._client,
                    id=self._dataset.id,
                    record_ids=[record.id for record in records[start:end]],
                )
            except Exception as e:
                raise RuntimeError("Failed to remove records from Argilla") from e

    def _fetch_records(self, offset: int, limit: int) -> "FeedbackRecordsModel":
        """Fetches a batch of records from Argilla."""

        return datasets_api_v1.get_records(
            client=self._client,
            id=self._dataset.id,
            include=self.include_as_query_params,
            offset=offset,
            limit=limit,
            response_status=self.response_status_as_query_string,
            metadata_filters=self.metadata_filters_as_query_strings,
            sort_by=self.__sort_by_query_strings,
        ).parsed

    def _has_filters(self) -> bool:
        """Returns whether the current `RemoteFeedbackRecords` is filtered or not."""
        return bool(self._response_status) or bool(self._metadata_filters)

    # TODO: define `List[ResponseStatusFilter]` and delegate `query_string` formatting to it
    @property
    def response_status_as_query_string(self) -> Optional[List[str]]:
        """Formats the `response_status` if any to the query string format. Otherwise, returns `None`."""
        return (
            [status.value if hasattr(status, "value") else status for status in self._response_status]
            if len(self._response_status) > 0
            else None
        )

    # TODO: define `List[MetadataFilter]` and delegate `query_string` formatting to it
    @property
    def metadata_filters_as_query_strings(self) -> Optional[List[str]]:
        """Formats the `metadata_filters` if any to the query string format. Otherwise, returns `None`."""
        return (
            [metadata_filter.query_string for metadata_filter in self._metadata_filters]
            if len(self._metadata_filters) > 0
            else None
        )

    # TODO: define `List[SortBy]` and delegate `query_string` formatting to it
    @property
    def __sort_by_query_strings(self) -> Optional[List[str]]:
        """Formats the `sort_by` if any to the query string format. Otherwise, returns `None`."""
        return [f"{sort_by.field}:{sort_by.order}" for sort_by in self._sort_by] if len(self._sort_by) > 0 else None

    @classmethod
    def _create_from_dataset(
        cls,
        new_ds: "RemoteFeedbackDataset",
        response_status: Optional[Union[ResponseStatusFilter, List[ResponseStatusFilter]]] = None,
        metadata_filters: Optional[Union["MetadataFilters", List["MetadataFilters"]]] = None,
        sort_by: Optional[List[SortBy]] = None,
    ):
        """Creates a new instance of `RemoteFeedbackRecords` with the given filters."""

        sort_by = sort_by or new_ds.records.sort_by
        metadata_filters = metadata_filters or new_ds.records.metadata_filters
        response_status = response_status or new_ds.records.response_status

        return cls(
            new_ds,
            sort_by=sort_by,
            metadata_filters=metadata_filters,
            response_status=response_status,
            with_vectors=new_ds.records._with_vectors,
        )

    def _validate_metadata_names(self):
        names = []
        if self.metadata_filters:
            names.extend([metadata_filter.name for metadata_filter in self.metadata_filters])
        if self.sort_by:
            names.extend([sort.metadata_name for sort in self.sort_by if sort.is_metadata_field])
        if names:
            helpers.validate_metadata_names(self.dataset, names)

    def _validate_vector_names(self):
        if not self._with_vectors or self._with_vectors == INCLUDE_ALL_VECTORS_PARAM:
            return

        if isinstance(self._with_vectors, str):
            self._with_vectors = [self._with_vectors]

        helpers.validate_vector_names(self.dataset, self._with_vectors)

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def find_similar(
        self,
        vector_name: str,
        value: Optional[List[float]] = None,
        record: Optional[RemoteFeedbackRecord] = None,
        max_results: int = 50,
    ) -> List[Tuple[RemoteFeedbackRecord, float]]:
        if bool(record) == bool(value):
            raise ValueError("Either 'record' or 'value' must be provided")

        try:
            response = datasets_api_v1.search_records(
                client=self._client,
                id=self.dataset.id,
                include=self.include_as_query_params,
                vector_query=FeedbackRecordsSearchVectorQuery(
                    name=vector_name,
                    record_id=record and record.id,
                    value=value,
                ),
                metadata_filters=self.metadata_filters_as_query_strings,
                response_status=self.response_status_as_query_string,
                limit=max_results,
            )
        except Exception as e:
            raise RuntimeError(f"Failed searching records for dataset with exception: {e}") from e

        question_id_to_name_map = self.dataset._question_id_to_name
        return [
            (
                RemoteFeedbackRecord.from_api(record_score.record, question_id_to_name=question_id_to_name_map),
                record_score.query_score,
            )
            for record_score in response.parsed.items
        ]

    @property
    def include_as_query_params(self) -> List[str]:
        include = ["responses", "suggestions"]  # default include

        if not self._with_vectors:
            return include

        if self._with_vectors == INCLUDE_ALL_VECTORS_PARAM:
            include.append("vectors")
        else:
            include.append(f"vectors:{','.join(self._with_vectors)}")

        return include


class RemoteFeedbackDataset(FeedbackDatasetBase[RemoteFeedbackRecord], MetricsMixin, UnificationMixin):
    # TODO: Call super method once the base init contains only commons init attributes
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
        allow_extra_metadata: bool = True,
        with_vectors: Union[Literal[INCLUDE_ALL_VECTORS_PARAM], List[str], None] = None,
    ) -> None:
        """Initializes a `RemoteFeedbackDataset` instance in Argilla.

        Note:
            This class is not intended to be initialised directly. Instead, use
            `FeedbackDataset.from_argilla` to get an instance of this class.

        Args:
            client: contains the `httpx.Client` instance that will be used to send requests to Argilla.
            id: contains the UUID of the dataset in Argilla.
            name: contains the name of the dataset in Argilla.
            workspace: contains the `Workspace` instance that the dataset belongs to in Argilla.
            created_at: contains the datetime when the dataset was created in Argilla.
            updated_at: contains the datetime when the dataset was last updated in Argilla.
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
        """

        self._fields = fields
        self._questions = questions
        self._guidelines = guidelines
        self._allow_extra_metadata = allow_extra_metadata

        self._client = client  # Required to be able to use `allowed_for_roles` decorator
        self._id = id
        self._name = name
        self._workspace = workspace
        self._created_at = created_at
        self._updated_at = updated_at

        self._records = RemoteFeedbackRecords(dataset=self, with_vectors=with_vectors)

    @property
    def guidelines(self) -> Optional[str]:
        return self._guidelines

    @property
    def allow_extra_metadata(self) -> bool:
        return self._allow_extra_metadata

    @property
    def fields(self) -> Union[List["AllowedRemoteFieldTypes"]]:
        return self._fields

    @property
    def questions(self) -> Union[List["AllowedRemoteQuestionTypes"]]:
        return self._questions

    @property
    def records(self) -> RemoteFeedbackRecords:
        """Returns an instance of `RemoteFeedbackRecords` that allows you to iterate over
        the records in the dataset. The records are fetched from Argilla on the fly and
        not stored in memory. You can also iterate over the records directly from the
        dataset instance.
        """
        return self._records

    @property
    def id(self) -> "UUID":
        """Returns the ID of the dataset in Argilla."""
        return self._id

    @property
    def name(self) -> str:
        """Returns the name of the dataset in Argilla."""
        return self._name

    @property
    def workspace(self) -> "Workspace":
        """Returns the workspace the dataset belongs to in Argilla."""
        return self._workspace

    @property
    def url(self) -> str:
        """Returns the URL of the dataset in Argilla."""
        return f"{self._client.base_url}/dataset/{self.id}/annotation-mode"

    @property
    def created_at(self) -> datetime:
        """Returns the datetime when the dataset was created in Argilla."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Returns the datetime when the dataset was last updated in Argilla."""
        return self._updated_at

    @property
    def _question_id_to_name(self) -> Dict["UUID", str]:
        return {question.id: question.name for question in self._questions}

    @property
    def _question_name_to_id(self) -> Dict[str, "UUID"]:
        return {question.name: question.id for question in self._questions}

    @property
    def metadata_properties(self) -> List["AllowedRemoteMetadataPropertyTypes"]:
        """Retrieves the `metadata_properties` of the current dataset from Argilla, and
        returns them if any, otherwise, it returns an empty list.
        """
        return ArgillaMetadataPropertiesMixin.list(client=self._client, dataset_id=self.id)

    @property
    def vectors_settings(self) -> List[RemoteVectorSettings]:
        """Retrieves the `vectors_settings` of the current dataset from Argilla"""
        response = datasets_api_v1.list_vectors_settings(client=self._client, id=self.id)

        return [RemoteVectorSettings.from_api(vector_settings) for vector_settings in response.parsed.items]

    def __repr__(self) -> str:
        """Returns a string representation of the dataset."""
        indent = "   "
        return (
            "RemoteFeedbackDataset("
            + textwrap.indent(f"\nid={self.id}", indent)
            + textwrap.indent(f"\nname={self.name}", indent)
            + textwrap.indent(f"\nworkspace={self.workspace}", indent)
            + textwrap.indent(f"\nurl={self.url}", indent)
            + textwrap.indent(f"\nfields={self.fields}", indent)
            + textwrap.indent(f"\nquestions={self.questions}", indent)
            + textwrap.indent(f"\nguidelines={self.guidelines}", indent)
            + textwrap.indent(f"\nmetadata_properties={self.metadata_properties}", indent)
            + textwrap.indent(f"\nvectors_settings={self.vectors_settings}", indent)
            + "\n)"
        )

    def __len__(self) -> int:
        """Returns the number of records in the dataset."""
        return self._records.__len__()

    def __iter__(self) -> Iterator[RemoteFeedbackRecord]:
        """Returns an iterator over the records in the dataset."""
        yield from self._records

    def __getitem__(self, key: Union[slice, int]) -> Union[RemoteFeedbackRecord, List[RemoteFeedbackRecord]]:
        """Returns the record(s) at the given index(es).

        Args:
            key: The index or slice to retrieve.

        Returns:
            The record(s) at the given index(es).
        """
        return self._records.__getitem__(key)

    def sort_by(self, sort: List[SortBy]) -> "RemoteFeedbackDataset":
        """Sorts the current `RemoteFeedbackDataset` based on the given sort fields and orders."""
        sorted_dataset = self._create_from_dataset(self)
        sorted_dataset._records = RemoteFeedbackRecords._create_from_dataset(sorted_dataset, sort_by=sort)

        return sorted_dataset

    def add_records(
        self,
        records: Union["FeedbackRecord", Dict[str, Any], List[Union["FeedbackRecord", Dict[str, Any]]]],
        show_progress: bool = True,
    ) -> None:
        """Adds the given records to the dataset and pushes those to Argilla.

        Args:
            records: can be a single `FeedbackRecord`, a list of `FeedbackRecord`,
                a single dictionary, or a list of dictionaries. If a dictionary is provided,
                it will be converted to a `FeedbackRecord` internally.
            show_progress: if `True`, shows a progress bar while pushing the records to
                Argilla. Defaults to `True`.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            ValueError: if the given records are neither: `FeedbackRecord`, list of
                `FeedbackRecord`, list of dictionaries as a record or dictionary as a
                record; or if the given records do not match the expected schema.
        """
        self._records.add(records=records, show_progress=show_progress)

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def find_similar_records(
        self,
        vector_name: str,
        value: Optional[List[float]] = None,
        record: Optional[RemoteFeedbackRecord] = None,
        max_results: int = 50,
    ) -> List[Tuple[RemoteFeedbackRecord, float]]:
        """Finds similar records to the given record in the dataset based on the given vector.

        Args:
            vector_name: a vector name to use for searching by similarity.
            value: an optional vector value to be used for searching by similarity. Defaults to None.
            record: an optional record to be used for searching by similarity. Defaults to None.
            max_results: the maximum number of results for the search. Defaults to 50.

        Returns:
            A list of tuples with each tuple including a record and a similarity score.
        """
        return self.records.find_similar(vector_name, value, record, max_results)

    def update_records(
        self,
        records: Union[RemoteFeedbackRecord, List[RemoteFeedbackRecord]],
        show_progress: bool = True,
    ) -> None:
        """Updates the given records in the dataset in Argilla.

        Args:
            records: the records to update in the dataset. Can be a single record or a
                list of records. The records need to be previously pushed to Argilla,
                otherwise they won't be updated.
            show_progress: if `True`, shows a progress bar while pushing the records to
                Argilla. Defaults to `True`.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
        """
        self._records.update(records=records, show_progress=show_progress)

    def delete_records(self, records: Union["RemoteFeedbackRecord", List["RemoteFeedbackRecord"]]) -> None:
        """Deletes the given records from the dataset in Argilla.

        Args:
            records: the records to delete from the dataset. Can be a single record or a list
                of records. But those need to be previously pushed to Argilla, otherwise
                they won't be deleted.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            RuntimeError: If the deletion of the records from Argilla fails.
        """
        self._records.delete(records=[records] if not isinstance(records, list) else records)

    def pull(self, max_records: Optional[int] = None) -> "FeedbackDataset":
        """Pulls the dataset from Argilla and returns a local instance of it.

        Args:
            max_records: the maximum number of records to pull from Argilla. Defaults to `None`.

        Returns:
            A local instance of the dataset which is a `FeedbackDataset` object.
        """
        # Importing here to avoid circular imports
        from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset

        instance = FeedbackDataset(
            fields=[field.to_local() for field in self.fields],
            questions=[question.to_local() for question in self.questions],
            guidelines=self.guidelines or None,
            metadata_properties=[metadata_property.to_local() for metadata_property in self.metadata_properties]
            or None,
            vectors_settings=[vector_settings.to_local() for vector_settings in self.vectors_settings] or None,
            allow_extra_metadata=self._allow_extra_metadata,
        )

        len_records = len(self._records)
        if len_records > 0:
            max_records = max_records or len_records
            records = [record.to_local() for record in self._records[:max_records]]
            instance.add_records(records=records)
        else:
            warnings.warn(
                "The dataset is empty, so no records will be added to the local instance.",
                UserWarning,
                stacklevel=1,
            )

        return instance

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def add_metadata_property(
        self, metadata_property: "AllowedMetadataPropertyTypes"
    ) -> "AllowedRemoteMetadataPropertyTypes":
        """Adds a new `metadata_property` to the current `FeedbackDataset` in Argilla.

        Note:
            Existing `FeedbackRecord`s if any will remain unchanged if those contain metadata
            named the same way as the `metadata_property`, but added before the
            `metadata_property` was added.

        Args:
            metadata_property: the metadata property to add to the current `FeedbackDataset`
                in Argilla.

        Returns:
            The newly added `metadata_property` to the current `FeedbackDataset` in Argilla.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            RuntimeError: if the `metadata_property` cannot be added to the current
                `FeedbackDataset` in Argilla.
        """
        self._unique_metadata_property(metadata_property=metadata_property)

        try:
            metadata_property = datasets_api_v1.add_metadata_property(
                client=self._client,
                id=self.id,
                metadata_property=metadata_property.to_server_payload(),
            ).parsed
        except Exception as e:
            raise RuntimeError(
                f"Failed while adding the `metadata_property={metadata_property}` to the current `FeedbackDataset` in Argilla with exception: {e}"
            ) from e

        # TODO(alvarobartt): structure better the mixins to be able to easily reuse those, here to avoid circular imports
        from argilla_v1.client.feedback.dataset.local.mixins import ArgillaMixin

        return ArgillaMixin._parse_to_remote_metadata_property(metadata_property=metadata_property, client=self._client)

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def update_metadata_properties(
        self,
        metadata_properties: Union["AllowedRemoteMetadataPropertyTypes", List["AllowedRemoteMetadataPropertyTypes"]],
    ) -> None:
        """Updates a list of `metadata_properties` in the current `FeedbackDataset` in Argilla.

        Note:
            All the `metadata_properties` provided must exist in Argilla in advance, and
            those will be pushed again to Argilla with the current values that they have,
            which ideally, should have been updated via assignment e.g. `metadata_property.title = \"...\"`.

        Args:
            metadata_properties: the metadata property/ies to update in the current `FeedbackDataset` in Argilla.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            RuntimeError: if the `metadata_properties` cannot be updated in the current
                `FeedbackDataset` in Argilla.
        """
        if not isinstance(metadata_properties, list):
            metadata_properties = [metadata_properties]

        for metadata_property in metadata_properties:
            try:
                ArgillaMetadataPropertiesMixin.update(
                    client=self._client,
                    metadata_property_id=metadata_property.id,
                    title=metadata_property.title,
                    visible_for_annotators=metadata_property.visible_for_annotators,
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed while updating the `metadata_property={metadata_property.name}` in the current"
                    f" `FeedbackDataset` in Argilla with exception: {e}"
                ) from e

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def delete_metadata_properties(
        self, metadata_properties: Union[str, List[str]]
    ) -> Union["AllowedMetadataPropertyTypes", List["AllowedMetadataPropertyTypes"]]:
        """Deletes a list of `metadata_properties` from the current `FeedbackDataset`
        in Argilla.

        Note:
            Existing `FeedbackRecord`s if any, will remain unchanged if those contain metadata
            named the same way as the `metadata_properties` to delete, but the validation will
            be removed as well as `metadata_property` index, which means one won't be able to
            use that for filtering.

        Args:
            metadata_properties: the metadata property/ies name/s to delete from the current
                `FeedbackDataset` in Argilla.

        Returns:
            The `metadata_property` or `metadata_properties` deleted from the current
            `FeedbackDataset` in Argilla, but using the local schema e.g. if you delete a
            `RemoteFloatMetadataProperty` this method will delete it from Argilla and will
            return a `FloatMetadataProperty` instance.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            RuntimeError: if the `metadata_properties` cannot be deleted from the current
                `FeedbackDataset` in Argilla.
        """
        if isinstance(metadata_properties, str):
            metadata_properties = [metadata_properties]

        existing_metadata_properties = self.metadata_properties
        existing_metadata_property_names = [
            metadata_property.name for metadata_property in existing_metadata_properties
        ]

        unexisting_metadata_properties = []
        for metadata_property in metadata_properties:
            if metadata_property not in existing_metadata_property_names:
                unexisting_metadata_properties.append(metadata_property)
        if len(unexisting_metadata_properties) > 0:
            raise ValueError(
                f"The following metadata properties do not exist in the current `FeedbackDataset` in Argilla: {unexisting_metadata_properties}."
                f" The existing metadata properties are: {existing_metadata_property_names}."
            )

        deleted_metadata_properties = []
        for metadata_property in existing_metadata_properties:
            if metadata_property.name in metadata_properties:
                ArgillaMetadataPropertiesMixin.delete(client=self._client, metadata_property_id=metadata_property.id)
                metadata_properties.remove(metadata_property.name)
                deleted_metadata_properties.append(metadata_property)
        return deleted_metadata_properties if len(deleted_metadata_properties) > 1 else deleted_metadata_properties[0]

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def add_vector_settings(self, vector_settings: VectorSettings) -> RemoteVectorSettings:
        """Adds a new vector settings to the current `FeedbackDataset` in Argilla.

        Args:
            vector_settings: the vector settings to add.

        Returns:
            The newly added vector settings to the current `FeedbackDataset` in Argilla.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            ValueError: if the vector settings with the given name already exists in the
                dataset in Argilla.
        """

        try:
            new_vector_settings = datasets_api_v1.add_vector_settings(
                client=self._client,
                id=self.id,
                title=vector_settings.title,
                name=vector_settings.name,
                dimensions=vector_settings.dimensions,
            ).parsed
        except AlreadyExistsApiError:
            raise ValueError(f"Vector settings with name {vector_settings.name!r} already exists.")
        return RemoteVectorSettings.from_api(new_vector_settings)

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def update_vectors_settings(
        self, vectors_settings: Union[RemoteVectorSettings, List[RemoteVectorSettings]]
    ) -> None:
        """Updates the given vector settings in the current `FeedbackDataset` in Argilla.

        Args:
            vectors_settings: the remote vectors settings to update. Must exist in Argilla in advance.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            RuntimeError: if the vector settings cannot be updated in the current
                `FeedbackDataset` in Argilla.
        """
        if isinstance(vectors_settings, RemoteVectorSettings):
            vectors_settings = [vectors_settings]

        for vector_settings in vectors_settings:
            try:
                vectors_settings_api_v1.update_vector_settings(
                    client=self._client,
                    id=vector_settings.id,
                    title=vector_settings.title,
                ).parsed
            except Exception as e:
                raise RuntimeError(
                    f"Failed while updating the `vector_settings={vector_settings.name}` in the current"
                    f" `FeedbackDataset` in Argilla with exception: {e}"
                ) from e

    def delete_vectors_settings(
        self, vectors_settings: Union[str, List[str]]
    ) -> Union[RemoteVectorSettings, List["RemoteVectorSettings"]]:
        """Deletes the given vectors settings from the current `FeedbackDataset` in Argilla.

        Args:
            vectors_settings: the name/s of the vectors settings to delete.

        Returns:
            The vectors settings deleted from the current `FeedbackDataset` in Argilla.

        Raises:
            ValueError: if the given vectors settings do not exist in the current
                `FeedbackDataset` in Argilla.
        """
        if isinstance(vectors_settings, str):
            vectors_settings = [vectors_settings]

        existing_vectors_settings_name = [vector_settings.name for vector_settings in self.vectors_settings]

        unexisting_vectors_settings = []
        for vector_settings in vectors_settings:
            if vector_settings not in existing_vectors_settings_name:
                unexisting_vectors_settings.append(vector_settings.name)
        if len(unexisting_vectors_settings) > 0:
            raise ValueError(
                f"The following vectors settings do not exist in the current `FeedbackDataset` in Argilla: {unexisting_vectors_settings}."
                f" The existing vectors settings are: {existing_vectors_settings_name}."
            )

        deleted_vectors_settings = []
        for vector_settings in self.vectors_settings:
            if vector_settings.name in vectors_settings:
                vectors_settings_api_v1.delete_vector_settings(client=self._client, id=vector_settings.id).parsed
                vectors_settings.remove(vector_settings.name)
                deleted_vectors_settings.append(vector_settings)
        return deleted_vectors_settings if len(deleted_vectors_settings) > 1 else deleted_vectors_settings[0]

    def filter_by(
        self,
        *,
        response_status: Optional[Union[ResponseStatusFilter, List[ResponseStatusFilter]]] = None,
        metadata_filters: Optional[Union["MetadataFilters", List["MetadataFilters"]]] = None,
    ) -> "RemoteFeedbackDataset":
        """Filters the current `RemoteFeedbackDataset` based on the `response_status` of
        the responses of the records in Argilla. This method creates a new class instance
        of `FilteredRemoteFeedbackDataset` with the given filters.

        Args:
            response_status: the response status/es to filter the dataset by. Can be
                one of: draft, pending, submitted, and discarded. Defaults to `None`.
            metadata_filters: the metadata filters to filter the dataset by. Can be
                one of: `TermsMetadataFilter`, `IntegerMetadataFilter`, and
                `FloatMetadataFilter`. Defaults to `None`.

        Returns:
            A new instance of `FilteredRemoteFeedbackDataset` with the given filters.
        """
        if not response_status and not metadata_filters:
            raise ValueError("At least one of `response_status` or `metadata_filters` must be provided.")

        filtered_dataset = RemoteFeedbackDataset._create_from_dataset(self)
        filtered_dataset._records = RemoteFeedbackRecords._create_from_dataset(
            filtered_dataset, response_status=response_status, metadata_filters=metadata_filters
        )

        return filtered_dataset

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def delete(self) -> None:
        """Deletes the current `FeedbackDataset` from Argilla. This method is just working
        if the user has either `owner` or `admin` role.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
            RuntimeError: if the `FeedbackDataset` cannot be deleted from Argilla.
        """
        try:
            datasets_api_v1.delete_dataset(client=self._client, id=self.id)
        except Exception as e:
            raise RuntimeError(f"Failed while deleting the `FeedbackDataset` from Argilla with exception: {e}") from e

    @classmethod
    def _create_from_dataset(cls, dataset: "RemoteFeedbackDataset") -> "RemoteFeedbackDataset":
        new_dataset = cls(
            client=dataset._client,
            id=dataset.id,
            name=dataset.name,
            workspace=dataset.workspace,
            created_at=dataset.created_at,
            updated_at=dataset.updated_at,
            fields=dataset.fields,
            questions=dataset.questions,
            guidelines=dataset.guidelines,
        )

        new_dataset._records = dataset.records

        return new_dataset

    def prepare_for_training(
        self,
        framework: Union[Framework, str],
        task: TrainingTaskTypes,
        train_size: Optional[float] = 1,
        test_size: Optional[float] = None,
        seed: Optional[int] = None,
        lang: Optional[str] = None,
    ) -> Any:
        """
        Prepares the dataset for training for a specific training framework and NLP task by splitting the dataset into train and test sets.

        Args:
            framework: the framework to use for training. Currently supported frameworks are: `transformers`, `peft`,
                `setfit`, `spacy`, `spacy-transformers`, `span_marker`, `spark-nlp`, `openai`, `trl`, `sentence-transformers`.
            task: the NLP task to use for training. Currently supported tasks are: `TrainingTaskForTextClassification`,
                `TrainingTaskForSFT`, `TrainingTaskForRM`, `TrainingTaskForPPO`, `TrainingTaskForDPO`, `TrainingTaskForSentenceSimilarity`.
            train_size: the size of the train set. If `None`, the whole dataset will be used for training.
            test_size: the size of the test set. If `None`, the whole dataset will be used for testing.
            seed: the seed to use for splitting the dataset into train and test sets.
            lang: the spaCy language to use for training. If `None`, the language of the dataset will be used.
        """
        warnings.warn(
            (
                "A local `FeedbackDataset` returned because "
                "`prepare_for_training` is not supported for `RemoteFeedbackDataset`. "
                "`RemoteFeedbackDataset`.pull().prepare_for_training(*args, **kwargs)` is applied."
            ),
            UserWarning,
        )
        local = self.pull()
        return local.prepare_for_training(
            framework=framework,
            task=task,
            train_size=train_size,
            test_size=test_size,
            seed=seed,
            lang=lang,
        )

    def push_to_argilla(
        self, name: str, workspace: Optional[Union[str, "Workspace"]] = None, show_progress: bool = False
    ) -> "RemoteFeedbackDataset":
        warnings.warn(
            "Already pushed datasets cannot be pushed to Argilla again because they are synced automatically.",
            UserWarning,
        )
        return self

    # TODO(@frascuchon): is this actually needed? what are the probabilities on a missmatch happening?
    def push_to_huggingface(self, repo_id: str, generate_card: Optional[bool] = True, *args, **kwargs) -> None:
        """Pushes the current `FeedbackDataset` to HuggingFace Hub.

        Note:
            The records from the `RemoteFeedbackDataset` are being pulled before pushing,
            to ensure that there's no missmatch while uploading those as those are lazily fetched.

        Args:
            repo_id: the ID of the HuggingFace repo to push the dataset to.
            generate_card: whether to generate a dataset card or not. Defaults to `True`.
        """
        warnings.warn(
            (
                "The dataset is first pulled locally and pushed to Hugging Face after because "
                "`push_to_huggingface` is not supported for a `RemoteFeedbackDataset`. "
                "`RemoteFeedbackDataset.pull().push_to_huggingface(...)` is applied."
            ),
            UserWarning,
        )
        dataset = self.pull()
        dataset.push_to_huggingface(repo_id=repo_id, generate_card=generate_card, *args, **kwargs)
