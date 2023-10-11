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
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from pydantic import ValidationError
from tqdm import trange

from argilla.client.feedback.constants import DELETE_DATASET_RECORDS_MAX_NUMBER, PUSHING_BATCH_SIZE
from argilla.client.feedback.dataset.remote.base import RemoteFeedbackDatasetBase, RemoteFeedbackRecordsBase
from argilla.client.feedback.dataset.remote.filtered import FilteredRemoteFeedbackDataset
from argilla.client.feedback.schemas.records import FeedbackRecord
from argilla.client.feedback.schemas.remote.records import RemoteFeedbackRecord
from argilla.client.sdk.users.models import UserRole
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.sdk.v1.datasets.models import FeedbackResponseStatusFilter
from argilla.client.utils import allowed_for_roles

if TYPE_CHECKING:
    from uuid import UUID

    import httpx

    from argilla.client.feedback.schemas.metadata import MetadataFilters
    from argilla.client.feedback.schemas.types import (
        AllowedMetadataPropertyTypes,
        AllowedRemoteFieldTypes,
        AllowedRemoteMetadataPropertyTypes,
        AllowedRemoteQuestionTypes,
    )
    from argilla.client.sdk.v1.datasets.models import FeedbackRecordsModel
    from argilla.client.workspaces import Workspace


class RemoteFeedbackRecords(RemoteFeedbackRecordsBase):
    def __init__(self, dataset: "RemoteFeedbackDataset") -> None:
        super().__init__(dataset=dataset)

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def __len__(self) -> int:
        """Returns the number of records in the current `FeedbackDataset` in Argilla."""
        try:
            response = datasets_api_v1.get_metrics(client=self._client, id=self._dataset.id)
        except Exception as e:
            raise Exception(
                f"Failed while getting the metrics from the current `FeedbackDataset` in Argilla with exception: {e}"
            ) from e
        return response.parsed.records.count

    def _fetch_records(self, offset: int, limit: int) -> "FeedbackRecordsModel":
        """Fetches a batch of records from Argilla."""
        return datasets_api_v1.get_records(
            client=self._client,
            id=self._dataset.id,
            offset=offset,
            limit=limit,
        ).parsed

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
        records = self._dataset._parse_and_validate_records(records)
        for i in trange(
            0, len(records), PUSHING_BATCH_SIZE, desc="Pushing records to Argilla...", disable=not show_progress
        ):
            datasets_api_v1.add_records(
                client=self._client,
                id=self._dataset.id,
                records=[
                    record.to_server_payload(self._question_name_to_id)
                    for record in records[i : i + PUSHING_BATCH_SIZE]
                ],
            )

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


class RemoteFeedbackDataset(RemoteFeedbackDatasetBase[RemoteFeedbackRecords]):
    records_cls = RemoteFeedbackRecords

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
        metadata_properties: Optional[List["AllowedRemoteMetadataPropertyTypes"]] = None,
        guidelines: Optional[str] = None,
        # TODO: uncomment once supported by the API
        # allow_extra_metadata: bool = False,
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
            metadata_properties=metadata_properties,
            guidelines=guidelines,
            # TODO: uncomment once supported by the API
            # allow_extra_metadata=allow_extra_metadata,
        )

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
        from argilla.client.feedback.dataset.mixins import ArgillaMixin

        metadata_property = ArgillaMixin._parse_to_remote_metadata_property(
            metadata_property=metadata_property, client=self._client
        )
        self._metadata_properties.append(metadata_property)
        self._metadata_properties_mapping[metadata_property.name] = metadata_property
        return metadata_property

    def filter_by(
        self,
        *,
        response_status: Optional[Union[FeedbackResponseStatusFilter, List[FeedbackResponseStatusFilter]]] = None,
        metadata_filters: Optional[Union["MetadataFilters", List["MetadataFilters"]]] = None,
    ) -> FilteredRemoteFeedbackDataset:
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

        if response_status:
            if not isinstance(response_status, list):
                response_status = [response_status]
            if not all(status in [arg.value for arg in FeedbackResponseStatusFilter] for status in response_status):
                raise ValueError(
                    f"Invalid `response_status={response_status}` provided, must be one"
                    f" of: {[arg.value for arg in FeedbackResponseStatusFilter]}"
                )

        if metadata_filters:
            if not isinstance(metadata_filters, list):
                metadata_filters = [metadata_filters]
            # TODO(alvarobartt): remove this when https://github.com/argilla-io/argilla/pull/3829 is merged
            if not hasattr(self, "_metadata_properties_mapping") or self._metadata_properties_mapping is None:
                self._metadata_properties_mapping = {
                    metadata_property.name: metadata_property for metadata_property in self._metadata_properties
                }
            if not all(
                metadata_filter.name in self._metadata_properties_mapping.keys() for metadata_filter in metadata_filters
            ):
                raise ValueError(
                    f"Invalid `metadata_filters=[{', '.join(metadata_filter.name for metadata_filter in metadata_filters)}`"
                    f" provided, must be one of: {self._metadata_properties_mapping.keys()}"
                )
            for metadata_filter in metadata_filters:
                metadata_property = self.metadata_property_by_name(name=metadata_filter.name)
                try:
                    metadata_property._validate_filter(metadata_filter=metadata_filter)
                except ValidationError as e:
                    raise ValueError(
                        f"Invalid `metadata_filter={metadata_filter}` provided for `metadata_property={metadata_property.name}`."
                    ) from e

        return FilteredRemoteFeedbackDataset(
            client=self._client,
            id=self.id,
            name=self.name,
            workspace=self.workspace,
            created_at=self.created_at,
            updated_at=self.updated_at,
            fields=self.fields,
            questions=self.questions,
            guidelines=self.guidelines,
            response_status=response_status,
            metadata_filters=metadata_filters,
        )

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
