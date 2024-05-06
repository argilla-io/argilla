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

import copy
from abc import ABC, abstractmethod
from typing import Dict, List, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.contexts import records
from argilla_server.models import Dataset, Record
from argilla_server.schemas.v1.records import RecordCreate, RecordUpdate, RecordUpsert
from argilla_server.schemas.v1.records_bulk import RecordsBulkCreate, RecordsBulkUpsert


class RecordValidatorBase(ABC):
    def __init__(self, record_change: Union[RecordCreate, RecordUpdate]):
        self._record_change = record_change

    @abstractmethod
    def validate_for(self, dataset: Dataset) -> None:
        pass

    def _validate_fields(self, dataset: Dataset) -> None:
        fields = self._record_change.fields or {}

        self._validate_required_fields(dataset, fields)
        self._validate_extra_fields(dataset, fields)

    def _validate_metadata(self, dataset: Dataset) -> None:
        metadata = self._record_change.metadata or {}
        for name, value in metadata.items():
            metadata_property = dataset.metadata_property_by_name(name)
            # TODO(@frascuchon): Create a MetadataPropertyValidator instead of using the parsed_settings
            if metadata_property and value is not None:
                try:
                    metadata_property.parsed_settings.check_metadata(value)
                except ValueError as e:
                    raise ValueError(
                        f"metadata is not valid: '{name}' metadata property validation failed because {e}"
                    ) from e

            elif metadata_property is None and not dataset.allow_extra_metadata:
                raise ValueError(
                    f"metadata is not valid: '{name}' metadata property does not exists for dataset '{dataset.id}' "
                    "and extra metadata is not allowed for this dataset"
                )

    def _validate_required_fields(self, dataset: Dataset, fields: Dict[str, str]) -> None:
        for field in dataset.fields:
            if field.required and not (field.name in fields and fields.get(field.name) is not None):
                raise ValueError(f"missing required value for field: {field.name!r}")

    def _validate_extra_fields(self, dataset: Dataset, fields: Dict[str, str]) -> None:
        fields_copy = copy.copy(fields)
        for field in dataset.fields:
            fields_copy.pop(field.name, None)
        if fields_copy:
            raise ValueError(f"found fields values for non configured fields: {list(fields_copy.keys())}")


class RecordCreateValidator(RecordValidatorBase):
    def __init__(self, record_create: RecordCreate):
        super().__init__(record_create)

    def validate_for(self, dataset: Dataset) -> None:
        self._validate_fields(dataset)
        self._validate_metadata(dataset)


class RecordUpdateValidator(RecordValidatorBase):
    def __init__(self, record_update: RecordUpdate):
        super().__init__(record_update)

    def validate_for(self, dataset: Dataset) -> None:
        self._validate_metadata(dataset)
        self._validate_duplicated_suggestions()

    def _validate_duplicated_suggestions(self):
        if not self._record_change.suggestions:
            return
        question_ids = [s.question_id for s in self._record_change.suggestions]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("found duplicate suggestions question IDs")


class RecordsBulkCreateValidator:
    def __init__(self, records_create: RecordsBulkCreate, db: AsyncSession):
        self._records_create = records_create
        self._db = db

    async def validate_for(self, dataset: Dataset) -> None:
        self._validate_dataset_is_ready(dataset)
        await self._validate_external_ids_are_not_present_in_db(dataset)
        self._validate_all_bulk_records(dataset, self._records_create.items)

    def _validate_dataset_is_ready(self, dataset: Dataset) -> None:
        if not dataset.is_ready:
            raise ValueError("records cannot be created for a non published dataset")

    async def _validate_external_ids_are_not_present_in_db(self, dataset: Dataset):
        external_ids = [r.external_id for r in self._records_create.items if r.external_id is not None]
        records_by_external_id = await records.fetch_records_by_external_ids_as_dict(self._db, dataset, external_ids)

        found_records = [str(external_id) for external_id in external_ids if external_id in records_by_external_id]
        if found_records:
            raise ValueError(f"found records with same external ids: {', '.join(found_records)}")

    def _validate_all_bulk_records(self, dataset: Dataset, records_create: List[RecordCreate]):
        for idx, record_create in enumerate(records_create):
            try:
                RecordCreateValidator(record_create).validate_for(dataset)
            except ValueError as ex:
                raise ValueError(f"record at position {idx} is not valid because {ex}") from ex


class RecordsBulkUpsertValidator:
    def __init__(
        self,
        records_upsert: RecordsBulkUpsert,
        db: AsyncSession,
        existing_records_by_external_id_or_record_id: Union[Dict[Union[str, UUID], Record], None] = None,
    ):
        self._db = db
        self._records_upsert = records_upsert
        self._existing_records_by_external_id_or_record_id = existing_records_by_external_id_or_record_id or {}

    def validate_for(self, dataset: Dataset) -> None:
        self.validate_dataset_is_ready(dataset)
        self._validate_all_bulk_records(dataset, self._records_upsert.items)

    def validate_dataset_is_ready(self, dataset: Dataset) -> None:
        if not dataset.is_ready:
            raise ValueError("records cannot be created or updated for a non published dataset")

    def _validate_all_bulk_records(self, dataset: Dataset, records_upsert: List[RecordUpsert]):
        for idx, record_upsert in enumerate(records_upsert):
            try:
                record = self._existing_records_by_external_id_or_record_id.get(
                    record_upsert.external_id or record_upsert.id
                )
                if record:
                    RecordUpdateValidator(RecordUpdate.parse_obj(record_upsert)).validate_for(dataset)
                else:
                    RecordCreateValidator(RecordCreate.parse_obj(record_upsert)).validate_for(dataset)
            except ValueError as ex:
                raise ValueError(f"record at position {idx} is not valid because {ex}") from ex
