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
import base64

from typing import Any
from uuid import uuid4
from typing_extensions import Self

from PIL import Image
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datasets import (
    Dataset as HFDataset,
    Image as HFImage,
    NamedSplit,
    Features,
    ClassLabel,
    load_dataset,
    features,
)

from argilla_server.enums import RecordStatus, ResponseStatus
from argilla_server.database import get_sync_db
from argilla_server.models.database import Dataset, Record, Question, MetadataProperty, VectorSettings
from argilla_server.search_engine import SearchEngine
from argilla_server.bulk.records_bulk import UpsertRecordsBulk
from argilla_server.api.schemas.v1.datasets import HubDatasetMapping
from argilla_server.api.schemas.v1.records import RecordUpsert as RecordUpsertSchema
from argilla_server.api.schemas.v1.records_bulk import RecordsBulkUpsert as RecordsBulkUpsertSchema
from argilla_server.api.schemas.v1.suggestions import SuggestionCreate

BATCH_SIZE = 100
RESET_ROW_IDX = -1

FEATURE_CLASS_LABEL_NO_LABEL = -1

DATA_URL_DEFAULT_IMAGE_FORMAT = "png"
DATA_URL_DEFAULT_IMAGE_MIMETYPE = "image/png"


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


RECORDS_YIELD_PER = 100


class HubDatasetExporter:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset

        # NOTE: Using this to bypass datasets generator cache.
        # self is the only parameter received by _rows_generator function. Setting a different value to self.version
        # is bypassing the datasets generator cache.
        self.version = uuid4()

    def export_to(self, name: str, subset: str, split: str, private: bool, token: str) -> None:
        hf_dataset = HFDataset.from_generator(self.rows_generator, split=NamedSplit(split), features=self.features())
        hf_dataset.push_to_hub(
            repo_id=name,
            config_name=subset,
            private=private,
            token=token,
        )

    def features(self) -> Features:
        return Features(
            self._features_attributes()
            | self._features_fields()
            | self._features_responses()
            | self._features_metadata()
            | self._features_vectors()
        )

    def _features_attributes(self) -> dict:
        return {
            "id": features.Value(dtype="string"),
            "status": ClassLabel(names=[rs.value for rs in RecordStatus]),
            "_server_id": features.Value(dtype="string"),
        }

    # TODO: Manage also custom type fields as feature
    def _features_fields(self) -> dict:
        features_fields = {}
        for field in self.dataset.fields:
            if field.is_image:
                features_fields[field.name] = HFImage()
            elif field.is_chat:
                features_fields[field.name] = [
                    {
                        "role": features.Value(dtype="string"),
                        "content": features.Value(dtype="string"),
                    }
                ]
            else:
                features_fields[field.name] = features.Value(dtype="string")

        return features_fields

    def _features_responses(self) -> dict:
        features_responses = {}
        for question in self.dataset.questions:
            feature_name = self._feature_name_for_response(question)
            feature_name_users = self._feature_name_for_response_users(question)
            feature_name_status = self._feature_name_for_response_status(question)

            if question.is_label_selection:
                features_responses[feature_name] = [ClassLabel(names=question.values)]
            elif question.is_multi_label_selection:
                features_responses[feature_name] = [[ClassLabel(names=question.values)]]
            elif question.is_rating:
                features_responses[feature_name] = [features.Value(dtype="int64")]
            elif question.is_ranking:
                features_responses[feature_name] = [
                    [
                        {
                            "value": features.Value(dtype="string"),
                            "rank": features.Value(dtype="int64"),
                        }
                    ]
                ]
            elif question.is_span:
                features_responses[feature_name] = [
                    [
                        {
                            "label": ClassLabel(names=question.values),
                            "start": features.Value(dtype="int64"),
                            "end": features.Value(dtype="int64"),
                        }
                    ]
                ]
            else:
                features_responses[feature_name] = [features.Value(dtype="string")]

            features_responses[feature_name_users] = [features.Value(dtype="string")]
            features_responses[feature_name_status] = [ClassLabel(names=[rs.value for rs in ResponseStatus])]

        return features_responses

    def _features_metadata(self) -> dict:
        features_metadata = {}
        for metadata_property in self.dataset.metadata_properties:
            feature_name = self._feature_name_for_metadata_property(metadata_property)

            if metadata_property.is_terms:
                features_metadata[feature_name] = [ClassLabel(names=metadata_property.values)]
            elif metadata_property.is_integer:
                features_metadata[feature_name] = features.Value(dtype="int64")
            elif metadata_property.is_float:
                features_metadata[feature_name] = features.Value(dtype="float64")

        return features_metadata

    def _features_vectors(self) -> dict:
        features_vectors = {}
        for vector_settings in self.dataset.vectors_settings:
            feature_name = self._feature_name_for_vector_settings(vector_settings)

            features_vectors[feature_name] = [features.Value(dtype="float64")]

        return features_vectors

    def rows_generator(self):
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

            for record in query.yield_per(RECORDS_YIELD_PER):
                yield self._record_to_row(record)

    def _record_to_row(self, record: Record) -> dict:
        return (
            self._row_attributes(record)
            | self._row_fields(record)
            | self._row_responses(record)
            | self._row_metadata(record)
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
            # TODO: If we are not managing custom fields we should
            # check it here and continue.

            field_value = record.fields.get(field.name)
            if field_value is None:
                continue

            if field.is_image:
                # TODO: What to do with images as URLs?
                row_fields[field.name] = {"bytes": data_url_to_bytes(field_value)}
            else:
                row_fields[field.name] = field_value

        return row_fields

    def _row_responses(self, record: Record) -> dict:
        row_responses = {}
        for question in self.dataset.questions:
            feature_name = self._feature_name_for_response(question)
            feature_name_users = self._feature_name_for_response_users(question)
            feature_name_status = self._feature_name_for_response_status(question)

            row_responses[feature_name] = []
            row_responses[feature_name_users] = []
            row_responses[feature_name_status] = []
            for response in record.responses:
                if response.values is not None:
                    response_value = response.values.get(question.name)
                    if response_value is not None:
                        row_responses[feature_name].append(response_value["value"])

                row_responses[feature_name_users].append(str(response.user_id))
                row_responses[feature_name_status].append(response.status)

        return row_responses

    def _row_metadata(self, record: Record) -> dict:
        row_metadata = {}
        for metadata_property in self.dataset.metadata_properties:
            if record.metadata_ is None:
                continue

            feature_name = self._feature_name_for_metadata_property(metadata_property)

            row_metadata[feature_name] = record.metadata_.get(metadata_property.name)

        return row_metadata

    def _row_vectors(self, record: Record) -> dict:
        row_vectors = {}
        for vector_settings in self.dataset.vectors_settings:
            feature_name = self._feature_name_for_vector_settings(vector_settings)

            row_vectors[feature_name] = record.vector_value_by_vector_settings(vector_settings)

        return row_vectors

    def _feature_name_for_response(self, question: Question) -> str:
        return f"{question.name}.responses"

    def _feature_name_for_response_users(self, question: Question) -> str:
        return f"{self._feature_name_for_response(question)}.users"

    def _feature_name_for_response_status(self, question: Question) -> str:
        return f"{self._feature_name_for_response(question)}.status"

    def _feature_name_for_metadata_property(self, metadata_property: MetadataProperty) -> str:
        return f"metadata.{metadata_property.name}"

    def _feature_name_for_vector_settings(self, vector_settings: VectorSettings) -> str:
        return f"vector.{vector_settings.name}"


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
