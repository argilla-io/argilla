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
import mimetypes
from abc import ABC
from typing import Dict, List, Union, Any, Optional
from urllib.parse import urlparse, ParseResult, ParseResultBytes

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.api.schemas.v1.chat import ChatFieldValue
from argilla_server.api.schemas.v1.records import RecordCreate, RecordUpsert
from argilla_server.api.schemas.v1.records_bulk import RecordsBulkCreate
from argilla_server.api.schemas.v1.responses import UserResponseCreate
from argilla_server.api.schemas.v1.suggestions import SuggestionCreate
from argilla_server.contexts import records
from argilla_server.errors.future.base_errors import UnprocessableEntityError
from argilla_server.models import Dataset, Record
from argilla_server.validators.responses import ResponseCreateValidator
from argilla_server.validators.suggestions import SuggestionCreateValidator
from argilla_server.validators.vectors import VectorValidator

IMAGE_FIELD_WEB_URL_MAX_LENGTH = 2038
IMAGE_FIELD_DATA_URL_MAX_LENGTH = 5_000_000
IMAGE_FIELD_DATA_URL_VALID_MIME_TYPES = [
    "image/avif",
    "image/gif",
    "image/ico",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/svg",
    "image/webp",
]
CHAT_FIELD_MAX_LENGTH = 500


class RecordValidatorBase(ABC):
    @classmethod
    def _validate_fields(cls, fields: dict, dataset: Dataset) -> None:
        cls._validate_non_empty_fields(fields=fields)
        cls._validate_required_fields(dataset=dataset, fields=fields)
        cls._validate_extra_fields(dataset=dataset, fields=fields)
        cls._validate_image_fields(dataset=dataset, fields=fields)
        cls._validate_chat_fields(dataset=dataset, fields=fields)
        cls._validate_custom_fields(dataset=dataset, fields=fields)

    @classmethod
    def _validate_non_empty_fields(cls, fields: Dict[str, str]) -> None:
        if not (isinstance(fields, dict) and len(fields) >= 1):
            raise UnprocessableEntityError("fields cannot be empty")

    @classmethod
    def _validate_required_fields(cls, dataset: Dataset, fields: Dict[str, str]) -> None:
        for field in dataset.fields:
            if field.required and not (field.name in fields and fields.get(field.name) is not None):
                raise UnprocessableEntityError(f"missing required value for field: {field.name!r}")

    @classmethod
    def _validate_extra_fields(cls, dataset: Dataset, fields: Dict[str, str]) -> None:
        fields_copy = copy.copy(fields)
        for field in dataset.fields:
            fields_copy.pop(field.name, None)
        if fields_copy:
            raise UnprocessableEntityError(f"found fields values for non configured fields: {list(fields_copy.keys())}")

    @classmethod
    def _validate_metadata(cls, metadata: dict, dataset: Dataset) -> None:
        metadata = metadata or {}

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

    @classmethod
    def _validate_image_fields(cls, dataset: Dataset, fields: Dict[str, str]) -> None:
        for field in filter(lambda field: field.is_image, dataset.fields):
            cls._validate_image_field(field.name, fields.get(field.name))

    @classmethod
    def _validate_chat_fields(cls, dataset: Dataset, fields: Dict[str, Any]) -> None:
        for field in filter(lambda field: field.is_chat, dataset.fields):
            cls._validate_chat_field(field.name, fields.get(field.name))

    @classmethod
    def _validate_image_field(cls, field_name: str, field_value: Union[str, None]) -> None:
        if field_value is None:
            return

        try:
            parse_result = urlparse(field_value)
        except ValueError:
            raise UnprocessableEntityError(f"image field {field_name!r} has an invalid URL value")

        if parse_result.scheme in ["http", "https"]:
            return cls._validate_web_url(field_name, field_value, parse_result)
        elif parse_result.scheme in ["data"]:
            return cls._validate_data_url(field_name, field_value, parse_result)
        else:
            raise UnprocessableEntityError(f"image field {field_name!r} has an invalid URL value")

    @classmethod
    def _validate_chat_field(cls, field_name: str, field_value: Any) -> None:
        # This validator is needed because pydantic can resolve values as Dicts since we have a new custom  field
        if field_value is None:
            return

        if not isinstance(field_value, list) or any(not isinstance(message, ChatFieldValue) for message in field_value):
            raise UnprocessableEntityError(f"chat field {field_name!r} value must be a list of messages")

    @staticmethod
    def _validate_web_url(
        field_name: str, field_value: str, parse_result: Union[ParseResult, ParseResultBytes]
    ) -> None:
        if not parse_result.netloc or not parse_result.path:
            raise UnprocessableEntityError(f"image field {field_name!r} has an invalid URL value")

        if len(field_value) > IMAGE_FIELD_WEB_URL_MAX_LENGTH:
            raise UnprocessableEntityError(
                f"image field {field_name!r} value is exceeding the maximum length of {IMAGE_FIELD_WEB_URL_MAX_LENGTH} characters for Web URLs"
            )

    @staticmethod
    def _validate_data_url(
        field_name: str, field_value: str, parse_result: Union[ParseResult, ParseResultBytes]
    ) -> None:
        if not parse_result.path:
            raise UnprocessableEntityError(f"image field {field_name!r} has an invalid URL value")

        if len(field_value) > IMAGE_FIELD_DATA_URL_MAX_LENGTH:
            raise UnprocessableEntityError(
                f"image field {field_name!r} value is exceeding the maximum length of {IMAGE_FIELD_DATA_URL_MAX_LENGTH} characters for Data URLs"
            )

        type, encoding = mimetypes.guess_type(field_value)
        if type not in IMAGE_FIELD_DATA_URL_VALID_MIME_TYPES:
            raise UnprocessableEntityError(
                f"image field {field_name!r} value is using an unsupported MIME type, supported MIME types are: {IMAGE_FIELD_DATA_URL_VALID_MIME_TYPES!r}"
            )

    @classmethod
    def _validate_custom_fields(cls, dataset: Dataset, fields: Dict[str, Any]) -> None:
        for field in filter(lambda field: field.is_custom, dataset.fields):
            cls._validate_custom_field(field.name, fields.get(field.name))

    @classmethod
    def _validate_custom_field(cls, name: str, value: Any) -> None:
        if value is None:
            return

        if not isinstance(value, dict):
            raise UnprocessableEntityError(f"custom field {name!r} value must be a dictionary")

    @classmethod
    def _validate_suggestions(cls, suggestions: List[SuggestionCreate], dataset: Dataset, record: Record):
        if not suggestions:
            return

        try:
            cls._validate_duplicated_suggestions(suggestions)

            for suggestion in suggestions:
                question = dataset.question_by_id(suggestion.question_id)

                if question is None:
                    raise UnprocessableEntityError(f"question id={suggestion.question_id} does not exists")

                SuggestionCreateValidator.validate(suggestion, question.parsed_settings, record)
        except (UnprocessableEntityError, ValueError, ValidationError) as ex:
            raise UnprocessableEntityError(f"record does not have valid suggestions: {ex}") from ex

    @classmethod
    def _validate_duplicated_suggestions(cls, suggestions: List[SuggestionCreate]):
        question_ids = [s.question_id for s in suggestions]

        if len(question_ids) != len(set(question_ids)):
            raise UnprocessableEntityError("found duplicate suggestions question IDs")

    @classmethod
    def _validate_vectors(cls, vectors: Optional[dict], dataset: Dataset):
        if not vectors:
            return

        try:
            for name, value in vectors.items():
                settings = dataset.vector_settings_by_name(name)

                if not settings:
                    raise UnprocessableEntityError(
                        f"vector with name={name} does not exist for dataset_id={dataset.id}"
                    )

                VectorValidator.validate(value, settings)
        except (UnprocessableEntityError, ValueError) as ex:
            raise UnprocessableEntityError(f"record does not have valid vectors: {ex}") from ex

    @classmethod
    async def _validate_responses(cls, responses: List[UserResponseCreate], dataset: Dataset, record: Record):
        from argilla_server.contexts.accounts import list_users_by_ids

        if not responses:
            return
        try:
            user_ids = [response_create.user_id for response_create in responses]
            users = await list_users_by_ids(dataset.current_async_session, set(user_ids))
            users_by_id = {user.id: user for user in users}

            for response_create in responses:
                if response_create.user_id not in users_by_id:
                    raise ValueError(f"user with id {response_create.user_id} not found")

                ResponseCreateValidator.validate(response_create, record)
        except (UnprocessableEntityError, ValueError) as ex:
            raise UnprocessableEntityError(f"record does not have valid responses: {ex}") from ex


class RecordCreateValidator(RecordValidatorBase):
    @classmethod
    async def validate(cls, record_create: RecordCreate, dataset: Dataset) -> None:
        record = Record(fields=record_create.fields, dataset=dataset)

        cls._validate_fields(record_create.fields, dataset)
        cls._validate_metadata(record_create.metadata, dataset)
        cls._validate_suggestions(record_create.suggestions, dataset, record=record)
        cls._validate_vectors(record_create.vectors, dataset)
        await cls._validate_responses(record_create.responses, dataset, record=record)


class RecordUpsertValidator(RecordValidatorBase):
    @classmethod
    async def validate(cls, record_upsert: RecordUpsert, dataset: Dataset, record: Optional[Record]) -> None:
        if record is None:
            cls._validate_fields(record_upsert.fields, dataset)
            record = Record(fields=record_upsert.fields, dataset=dataset)

        cls._validate_metadata(record_upsert.metadata, dataset)
        cls._validate_vectors(record_upsert.vectors, dataset)

        cls._validate_suggestions(record_upsert.suggestions, dataset, record=record)
        await cls._validate_responses(record_upsert.responses, dataset, record=record)


class RecordsBulkCreateValidator:
    @classmethod
    async def validate(cls, db: AsyncSession, records_create: RecordsBulkCreate, dataset: Dataset) -> None:
        cls._validate_dataset_is_ready(dataset)
        await cls._validate_external_ids_are_not_present_in_db(db, records_create, dataset)
        await cls._validate_all_bulk_records(dataset, records_create.items)

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
    async def _validate_all_bulk_records(dataset: Dataset, records_create: List[RecordCreate]):
        for idx, record_create in enumerate(records_create):
            try:
                await RecordCreateValidator.validate(record_create, dataset)
            except (UnprocessableEntityError, ValueError) as ex:
                raise UnprocessableEntityError(f"Record at position {idx} is not valid because {ex}") from ex
