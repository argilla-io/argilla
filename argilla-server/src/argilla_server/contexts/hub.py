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

import io
import os
import base64
import json

from uuid import uuid4
from pathlib import Path
from typing import Any, Optional, List
from typing_extensions import Self
from tempfile import TemporaryDirectory

from PIL import Image
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from huggingface_hub import HfApi, DatasetCard, DatasetCardData
from datasets import Dataset as HFDataset, NamedSplit, load_dataset, features

from argilla_server.contexts import info
from argilla_server.database import get_sync_db
from argilla_server.models.database import Dataset, Record, Field, Question, MetadataProperty, VectorSettings
from argilla_server.search_engine import SearchEngine
from argilla_server.bulk.records_bulk import UpsertRecordsBulk
from argilla_server.api.schemas.v1.datasets import (
    HubDatasetMapping,
    Dataset as DatasetSchema,
    DatasetDistribution as DatasetDistributionSchema,
)
from argilla_server.api.schemas.v1.fields import Field as FieldSchema
from argilla_server.api.schemas.v1.questions import Question as QuestionSchema
from argilla_server.api.schemas.v1.records import RecordUpsert as RecordUpsertSchema
from argilla_server.api.schemas.v1.records_bulk import RecordsBulkUpsert as RecordsBulkUpsertSchema
from argilla_server.api.schemas.v1.metadata_properties import MetadataProperty as MetadataPropertySchema
from argilla_server.api.schemas.v1.vector_settings import VectorSettings as VectorSettingsSchema
from argilla_server.api.schemas.v1.suggestions import SuggestionCreate

BATCH_SIZE = 100
RESET_ROW_IDX = -1

FEATURE_CLASS_LABEL_NO_LABEL = -1

DATA_URL_DEFAULT_IMAGE_FORMAT = "png"
DATA_URL_DEFAULT_IMAGE_MIMETYPE = "image/png"

HUB_RECORDS_YIELD_PER = 100
HUB_DATASET_CARD_TEMPLATE_PATH = os.path.join(Path(__file__).parent, "hub_templates", "README.md.jinja2")


class HubDataset:
    def __init__(self, name: str, subset: str, split: str, mapping: HubDatasetMapping):
        self.dataset = load_dataset(path=name, name=subset, split=split, streaming=True)
        self.split = split
        self.mapping = mapping
        self.mapping_feature_names = mapping.sources
        self.row_idx = RESET_ROW_IDX

    @property
    def features(self) -> dict:
        return self.dataset.features

    def take(self, n: int) -> Self:
        self.dataset = self.dataset.take(n)

        return self

    async def import_to(self, db: AsyncSession, search_engine: SearchEngine, dataset: Dataset) -> None:
        if not dataset.is_ready:
            raise Exception("it's not possible to import records to a non published dataset")

        self._reset_row_idx()

        batched_dataset = self.dataset.batch(batch_size=BATCH_SIZE)
        for batch in batched_dataset:
            await self._import_batch_to(db, search_engine, batch, dataset)

    def _reset_row_idx(self) -> None:
        self.row_idx = RESET_ROW_IDX

    def _next_row_idx(self) -> int:
        self.row_idx += 1

        return self.row_idx

    async def _import_batch_to(
        self, db: AsyncSession, search_engine: SearchEngine, batch: dict, dataset: Dataset
    ) -> None:
        batch_size = len(next(iter(batch.values())))

        items = []
        for i in range(batch_size):
            items.append(self._row_to_record_schema(self._batch_index_to_row(batch, i), dataset))

        await UpsertRecordsBulk(db, search_engine).upsert_records_bulk(
            dataset,
            RecordsBulkUpsertSchema(items=items),
            raise_on_error=False,
        )

    def _batch_index_to_row(self, batch: dict, index: int) -> dict:
        row = {}
        for feature_name, values in batch.items():
            if not feature_name in self.mapping_feature_names:
                continue

            row[feature_name] = self._cast_feature_value(self.features[feature_name], values[index])

        return row

    def _cast_feature_value(self, feature: Any, value: Any) -> Any:
        if isinstance(feature, features.ClassLabel):
            if value == FEATURE_CLASS_LABEL_NO_LABEL:
                return None
            else:
                return feature.int2str(value)
        elif isinstance(feature, features.Sequence):
            return [self._cast_feature_value(feature.feature, v) for v in value]
        elif isinstance(feature, features.Image) and isinstance(value, Image.Image):
            return pil_image_to_data_url(value)
        else:
            return value

    def _row_to_record_schema(self, row: dict, dataset: Dataset) -> RecordUpsertSchema:
        return RecordUpsertSchema(
            id=None,
            external_id=self._row_external_id(row),
            fields=self._row_fields(row, dataset),
            metadata=self._row_metadata(row, dataset),
            suggestions=self._row_suggestions(row, dataset),
            responses=None,
            vectors=None,
        )

    def _row_external_id(self, row: dict) -> str:
        if not self.mapping.external_id:
            return f"{self.split}_{self._next_row_idx()}"

        return row[self.mapping.external_id]

    def _row_fields(self, row: dict, dataset: Dataset) -> dict:
        fields = {}
        for mapping_field in self.mapping.fields:
            value = row[mapping_field.source]
            field = dataset.field_by_name(mapping_field.target)
            if value is None or not field:
                continue

            if field.is_text and value is not None:
                value = str(value)

            fields[field.name] = value

        return fields

    def _row_metadata(self, row: dict, dataset: Dataset) -> dict:
        metadata = {}
        for mapping_metadata in self.mapping.metadata:
            value = row[mapping_metadata.source]
            metadata_property = dataset.metadata_property_by_name(mapping_metadata.target)
            if value is None or not metadata_property:
                continue

            metadata[metadata_property.name] = value

        return metadata

    def _row_suggestions(self, row: dict, dataset: Dataset) -> list:
        suggestions = []
        for mapping_suggestion in self.mapping.suggestions:
            value = row[mapping_suggestion.source]
            question = dataset.question_by_name(mapping_suggestion.target)
            if value is None or not question:
                continue

            if question.is_text or question.is_label_selection:
                value = str(value)

            if question.is_multi_label_selection:
                if isinstance(value, list):
                    value = [str(v) for v in value]
                else:
                    value = [str(value)]

            if question.is_rating:
                value = int(value)

            suggestions.append(
                SuggestionCreate(
                    question_id=question.id,
                    value=value,
                    type=None,
                    agent=None,
                    score=None,
                ),
            )

        return suggestions


class HubDatasetSettingsSchema(BaseModel):
    guidelines: Optional[str] = None
    allow_extra_metadata: bool
    distribution: DatasetDistributionSchema
    # TODO: Add missing mapping attribute. Discuss it with Ben.
    fields: List[FieldSchema]
    questions: List[QuestionSchema]
    metadata: List[MetadataPropertySchema]
    vectors: List[VectorSettingsSchema]


class HubDatasetExporter:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset

        # NOTE: Using this to bypass datasets generator cache.
        # self is the only parameter received by _rows_generator function. Setting a different value to
        # self.cache_version is bypassing the datasets generator cache.
        self.cache_version = uuid4()

    def export_to(self, name: str, subset: str, split: str, private: bool, token: str) -> None:
        hf_dataset = HFDataset.from_generator(self._rows_generator, split=NamedSplit(split))
        hf_dataset.push_to_hub(
            repo_id=name,
            config_name=subset,
            private=private,
            token=token,
        )

        self._push_extra_files_to_hub(repo_id=name, token=token)

    def _rows_generator(self):
        for session in get_sync_db():
            query = (
                session.query(Record)
                .filter_by(dataset_id=self.dataset.id)
                .order_by(Record.inserted_at.asc())
                .options(
                    selectinload(Record.responses),
                    selectinload(Record.vectors),
                )
            )

            for record in query.yield_per(HUB_RECORDS_YIELD_PER):
                yield self._record_to_row(record)

    def _record_to_row(self, record: Record) -> dict:
        return (
            self._row_attributes(record)
            | self._row_fields(record)
            | self._row_responses(record)
            | self._row_metadata(record)
            # TODO: Is not possible to add extra metadata because the features need to be specified (even if with NULL) for all records.
            # | self._row_extra_metadata(record)
            | self._row_vectors(record)
        )

    def _row_attributes(self, record: Record) -> dict:
        return {
            "id": record.external_id,
            "status": record.status,
            "_server_id": str(record.id),
        }

    def _row_fields(self, record: Record) -> dict:
        row_fields = {}
        for field in self.dataset.fields:
            feature_name = self._feature_name_for_field(field)
            feature_value = record.fields.get(field.name)

            if field.is_image and feature_value is not None and feature_value.startswith("data:"):
                row_fields[feature_name] = Image.open(io.BytesIO(data_url_to_bytes(feature_value)))
            else:
                row_fields[feature_name] = feature_value

        return row_fields

    def _row_responses(self, record: Record) -> dict:
        row_responses = {}
        for question in self.dataset.questions:
            feature_name = self._feature_name_for_response(question)
            feature_name_users = self._feature_name_for_response_users(question)
            feature_name_status = self._feature_name_for_response_status(question)

            row_responses[feature_name] = None
            row_responses[feature_name_users] = None
            row_responses[feature_name_status] = None
            for response in record.responses:
                response_values = response.values or {}
                response_value = response_values.get(question.name, {})

                feature_value = response_value.get("value")

                if row_responses[feature_name] is None:
                    row_responses[feature_name] = []
                    row_responses[feature_name_users] = []
                    row_responses[feature_name_status] = []

                row_responses[feature_name].append(feature_value)
                row_responses[feature_name_users].append(str(response.user_id))
                row_responses[feature_name_status].append(response.status)

        return row_responses

    def _row_metadata(self, record: Record) -> dict:
        row_metadata = {}

        record_metadata = record.metadata_ or {}
        for metadata_property in self.dataset.metadata_properties:
            feature_name = self._feature_name_for_metadata_property(metadata_property)
            feature_value = record_metadata.get(metadata_property.name)

            if metadata_property.is_terms and not isinstance(feature_value, list):
                feature_value = [feature_value]

            row_metadata[feature_name] = feature_value

        return row_metadata

    def _row_extra_metadata(self, record: Record) -> dict:
        if not self.dataset.allow_extra_metadata:
            return {}

        row_extra_metadata = {}
        record_metadata = record.metadata_ or {}
        metadata_properties_names = [metadata_property.name for metadata_property in self.dataset.metadata_properties]
        for metadata_name, metadata_value in record_metadata.items():
            if metadata_name in metadata_properties_names:
                continue

            feature_name = self._feature_name_for_extra_metadata(metadata_name)
            feature_value = metadata_value

            row_extra_metadata[feature_name] = feature_value

        return row_extra_metadata

    def _row_vectors(self, record: Record) -> dict:
        row_vectors = {}
        for vector_settings in self.dataset.vectors_settings:
            feature_name = self._feature_name_for_vector_settings(vector_settings)
            feature_value = record.vector_value_by_vector_settings(vector_settings)

            row_vectors[feature_name] = feature_value

        return row_vectors

    def _feature_name_for_field(self, field: Field) -> str:
        return field.name

    def _feature_name_for_response(self, question: Question) -> str:
        return f"{question.name}.responses"

    def _feature_name_for_response_users(self, question: Question) -> str:
        return f"{self._feature_name_for_response(question)}.users"

    def _feature_name_for_response_status(self, question: Question) -> str:
        return f"{self._feature_name_for_response(question)}.status"

    def _feature_name_for_metadata_property(self, metadata_property: MetadataProperty) -> str:
        return f"metadata.{metadata_property.name}"

    def _feature_name_for_extra_metadata(self, extra_metadata_name: str) -> str:
        return f"metadata.{extra_metadata_name}"

    def _feature_name_for_vector_settings(self, vector_settings: VectorSettings) -> str:
        return f"vector.{vector_settings.name}"

    def _push_extra_files_to_hub(self, repo_id: str, token: str) -> None:
        hf_api = HfApi(token=token)

        with TemporaryDirectory() as temporary_directory:
            argilla_directory = os.path.join(temporary_directory, ".argilla")
            os.makedirs(argilla_directory)

            self._create_version_file(argilla_directory)
            self._create_dataset_file(argilla_directory)
            self._create_settings_file(argilla_directory)
            self._create_readme_file(temporary_directory, repo_id)

            hf_api.upload_folder(
                repo_id=repo_id,
                repo_type="dataset",
                folder_path=temporary_directory,
            )

    def _create_version_file(self, directory: str) -> None:
        with open(os.path.join(directory, "version.json"), "w") as file:
            file.write(json.dumps({"argilla": info.argilla_version()}, indent=2))

    def _create_dataset_file(self, directory: str) -> None:
        with open(os.path.join(directory, "dataset.json"), "w") as file:
            file.write(DatasetSchema.model_validate(self.dataset).model_dump_json(indent=2))

    def _create_settings_file(self, directory: str) -> None:
        with open(os.path.join(directory, "settings.json"), "w") as file:
            dataset_settings = HubDatasetSettingsSchema(
                guidelines=self.dataset.guidelines,
                allow_extra_metadata=self.dataset.allow_extra_metadata,
                distribution=DatasetDistributionSchema.model_validate(self.dataset.distribution),
                fields=[FieldSchema.model_validate(field) for field in self.dataset.fields],
                questions=[QuestionSchema.model_validate(question) for question in self.dataset.questions],
                metadata=[
                    MetadataPropertySchema.model_validate(metadata_property)
                    for metadata_property in self.dataset.metadata_properties
                ],
                vectors=[
                    VectorSettingsSchema.model_validate(vector_settings)
                    for vector_settings in self.dataset.vectors_settings
                ],
            )

            file.write(dataset_settings.model_dump_json(indent=2))

    def _create_readme_file(self, directory: str, repo_id: str) -> None:
        card = DatasetCard.from_template(
            card_data=DatasetCardData(
                # size_categories=size_categories_parser(dataset_size),
                tags=["rlfh", "argilla", "human-feedback"],
            ),
            template_path=HUB_DATASET_CARD_TEMPLATE_PATH,
            repo_id=repo_id,
            argilla_fields=self.dataset.fields,
            argilla_questions=self.dataset.questions,
            argilla_guidelines=self.dataset.guidelines or None,
            argilla_vectors_settings=self.dataset.vectors_settings or None,
            argilla_metadata_properties=self.dataset.metadata_properties,
            # argilla_record=sample_argilla_record.to_dict(),
            # huggingface_record=sample_huggingface_record,
        )

        card.save(os.path.join(directory, "README.md"))


def pil_image_to_data_url(image: Image.Image):
    buffer = io.BytesIO()

    image_format = image.format or DATA_URL_DEFAULT_IMAGE_FORMAT
    image_mimetype = image.get_format_mimetype() if image.format else DATA_URL_DEFAULT_IMAGE_MIMETYPE

    image.convert("RGB").save(buffer, format=image_format)

    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:{image_mimetype};base64,{base64_image}"


def data_url_to_bytes(data_url: str):
    header, encoded = data_url.split(",", 1)

    return base64.b64decode(encoded)
