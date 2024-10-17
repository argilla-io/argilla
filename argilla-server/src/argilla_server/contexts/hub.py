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

from typing import Union
from typing_extensions import Self

from PIL import Image
from datasets import load_dataset
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.models.database import Dataset
from argilla_server.search_engine import SearchEngine
from argilla_server.bulk.records_bulk import UpsertRecordsBulk
from argilla_server.api.schemas.v1.datasets import HubDatasetMapping
from argilla_server.api.schemas.v1.records import RecordUpsert as RecordUpsertSchema
from argilla_server.api.schemas.v1.records_bulk import RecordsBulkUpsert as RecordsBulkUpsertSchema
from argilla_server.api.schemas.v1.suggestions import SuggestionCreate

BATCH_SIZE = 100
RESET_ROW_IDX = -1

FEATURE_TYPE_IMAGE = "Image"
FEATURE_TYPE_CLASS_LABEL = "ClassLabel"

DATA_URL_DEFAULT_IMAGE_FORMAT = "png"
DATA_URL_DEFAULT_IMAGE_MIMETYPE = "image/png"

FEATURE_CLASS_LABEL_NO_LABEL = -1


class HubDataset:
    def __init__(self, name: str, subset: str, split: str, mapping: HubDatasetMapping):
        self.dataset = load_dataset(path=name, name=subset, split=split, streaming=True)
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

            value = values[index]
            feature = self.features[feature_name]

            if feature._type == FEATURE_TYPE_CLASS_LABEL:
                if value == FEATURE_CLASS_LABEL_NO_LABEL:
                    row[feature_name] = None
                else:
                    row[feature_name] = feature.int2str(value)
            elif feature._type == FEATURE_TYPE_IMAGE and isinstance(value, Image.Image):
                row[feature_name] = pil_image_to_data_url(value)
            else:
                row[feature_name] = value

        return row

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
            return str(self._next_row_idx())

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


def pil_image_to_data_url(image: Image.Image):
    buffer = io.BytesIO()

    image_format = image.format or DATA_URL_DEFAULT_IMAGE_FORMAT
    image_mimetype = image.get_format_mimetype() if image.format else DATA_URL_DEFAULT_IMAGE_MIMETYPE

    image.convert("RGB").save(buffer, format=image_format)

    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:{image_mimetype};base64,{base64_image}"
