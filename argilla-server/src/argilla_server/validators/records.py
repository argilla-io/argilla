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

from argilla_server.api.schemas.v1.records import RecordCreate, RecordUpdate, RecordUpsert
from argilla_server.api.schemas.v1.records_bulk import RecordsBulkCreate, RecordsBulkUpsert
from argilla_server.contexts import records
from argilla_server.errors.future.base_errors import UnprocessableEntityError
from argilla_server.models import Dataset, Record


class RecordValidatorBase(ABC):
    @classmethod
    @abstractmethod
    def validate(cls, record: Union[RecordCreate, RecordUpdate], dataset: Dataset) -> None:
        pass

    @classmethod
    def _validate_fields(cls, record: Union[RecordCreate, RecordUpdate], dataset: Dataset) -> None:
        fields = record.fields or {}

        cls._validate_required_fields(dataset, fields)
        cls._validate_extra_fields(dataset, fields)

    @staticmethod
    def _validate_required_fields(dataset: Dataset, fields: Dict[str, str]) -> None:
        for field in dataset.fields:
            if field.required and not (field.name in fields and fields.get(field.name) is not None):
                raise UnprocessableEntityError(f"missing required value for field: {field.name!r}")

    @staticmethod
    def _validate_extra_fields(dataset: Dataset, fields: Dict[str, str]) -> None:
        fields_copy = copy.copy(fields)
        for field in dataset.fields:
            fields_copy.pop(field.name, None)
        if fields_copy:
            raise UnprocessableEntityError(f"found fields values for non configured fields: {list(fields_copy.keys())}")

    @staticmethod
    def _validate_metadata(record: Union[RecordCreate, RecordUpdate], dataset: Dataset) -> None:
        metadata = record.metadata or {}
        for name, value in metadata.items():
            metadata_property = dataset.metadata_property_by_name(name)
            # TODO(@frascuchon): Create a MetadataPropertyValidator instead of using the parsed_settings
            if metadata_property and value is not None:
                try:
                    metadata_property.parsed_settings.check_metadata(value)
                except UnprocessableEntityError as e:
                    raise UnprocessableEntityError(
                        f"metadata is not valid: '{name}' metadata property validation failed because {e}"
                    ) from e

            elif metadata_property is None and not dataset.allow_extra_metadata:
                raise UnprocessableEntityError(
                    f"metadata is not valid: '{name}' metadata property does not exists for dataset '{dataset.id}' "
                    "and extra metadata is not allowed for this dataset"
                )


class RecordCreateValidator(RecordValidatorBase):
    @classmethod
    def validate(cls, record: RecordCreate, dataset: Dataset) -> None:
        cls._validate_fields(record, dataset)
        cls._validate_metadata(record, dataset)


class RecordUpdateValidator(RecordValidatorBase):
    @classmethod
    def validate(cls, record: RecordUpdate, dataset: Dataset) -> None:
        cls._validate_metadata(record, dataset)
        cls._validate_duplicated_suggestions(record)

    @staticmethod
    def _validate_duplicated_suggestions(record: RecordUpdate):
        if not record.suggestions:
            return
        question_ids = [s.question_id for s in record.suggestions]
        if len(question_ids) != len(set(question_ids)):
            raise UnprocessableEntityError("found duplicate suggestions question IDs")


class RecordsBulkCreateValidator:
    @classmethod
    async def validate(cls, db: AsyncSession, records_create: RecordsBulkCreate, dataset: Dataset) -> None:
        cls._validate_dataset_is_ready(dataset)
        await cls._validate_external_ids_are_not_present_in_db(db, records_create, dataset)
        cls._validate_all_bulk_records(dataset, records_create.items)

    @staticmethod
    def _validate_dataset_is_ready(dataset: Dataset) -> None:
        if not dataset.is_ready:
            raise UnprocessableEntityError("records cannot be created for a non published dataset")

    @staticmethod
    async def _validate_external_ids_are_not_present_in_db(
        db: AsyncSession, records_create: RecordsBulkCreate, dataset: Dataset
    ):
        external_ids = [r.external_id for r in records_create.items if r.external_id is not None]
        records_by_external_id = await records.fetch_records_by_external_ids_as_dict(db, dataset, external_ids)

        found_records = [str(external_id) for external_id in external_ids if external_id in records_by_external_id]
        if found_records:
            raise UnprocessableEntityError(f"found records with same external ids: {', '.join(found_records)}")

    @staticmethod
    def _validate_all_bulk_records(dataset: Dataset, records_create: List[RecordCreate]):
        for idx, record_create in enumerate(records_create):
            try:
                RecordCreateValidator.validate(record_create, dataset)
            except UnprocessableEntityError as ex:
                raise UnprocessableEntityError(f"record at position {idx} is not valid because {ex}") from ex


class RecordsBulkUpsertValidator:
    @classmethod
    def validate(
        cls,
        records_upsert: RecordsBulkUpsert,
        dataset: Dataset,
        existing_records_by_external_id_or_record_id: Union[Dict[Union[str, UUID], Record], None] = None,
    ) -> None:
        cls._validate_dataset_is_ready(dataset)
        cls._validate_all_bulk_records(dataset, records_upsert.items, existing_records_by_external_id_or_record_id)

    @staticmethod
    def _validate_dataset_is_ready(dataset: Dataset) -> None:
        if not dataset.is_ready:
            raise UnprocessableEntityError("records cannot be created or updated for a non published dataset")

    @staticmethod
    def _validate_all_bulk_records(
        dataset: Dataset,
        records_upsert: List[RecordUpsert],
        existing_records_by_external_id_or_record_id: Union[Dict[Union[str, UUID], Record], None] = None,
    ):
        existing_records_by_external_id_or_record_id = existing_records_by_external_id_or_record_id or {}
        for idx, record_upsert in enumerate(records_upsert):
            try:
                record = existing_records_by_external_id_or_record_id.get(
                    record_upsert.id
                ) or existing_records_by_external_id_or_record_id.get(record_upsert.external_id)

                if record:
                    RecordUpdateValidator.validate(RecordUpdate.parse_obj(record_upsert), dataset)
                else:
                    RecordCreateValidator.validate(RecordCreate.parse_obj(record_upsert), dataset)
            except (UnprocessableEntityError, ValueError) as ex:
                raise UnprocessableEntityError(f"record at position {idx} is not valid because {ex}") from ex
