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


class HubDataset:
    def __init__(self, name: str, subset: str, split: str, mapping: HubDatasetMapping):
        self.dataset = load_dataset(path=name, name=subset, split=split)
        self.mapping = mapping
        self.iterable_dataset = self.dataset.to_iterable_dataset()
        self.row_idx = RESET_ROW_IDX

    @property
    def num_rows(self) -> int:
        return self.dataset.num_rows

    def take(self, n: int) -> Self:
        self.iterable_dataset = self.iterable_dataset.take(n)

        return self

    async def import_to(self, db: AsyncSession, search_engine: SearchEngine, dataset: Dataset) -> None:
        if not dataset.is_ready:
            raise Exception("it's not possible to import records to a non published dataset")

        self._reset_row_idx()

        batched_dataset = self.iterable_dataset.batch(batch_size=BATCH_SIZE)
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
            items.append(self._batch_row_to_record_schema(batch, i, dataset))

        await UpsertRecordsBulk(db, search_engine).upsert_records_bulk(dataset, RecordsBulkUpsertSchema(items=items))

    def _batch_row_to_record_schema(self, batch: dict, index: int, dataset: Dataset) -> RecordUpsertSchema:
        return RecordUpsertSchema(
            id=None,
            external_id=self._batch_row_external_id(batch, index),
            fields=self._batch_row_fields(batch, index, dataset),
            metadata=self._batch_row_metadata(batch, index, dataset),
            suggestions=self._batch_row_suggestions(batch, index, dataset),
            responses=None,
            vectors=None,
        )

    def _batch_row_external_id(self, batch: dict, index: int) -> str:
        if not self.mapping.external_id:
            return str(self._next_row_idx())

        return batch[self.mapping.external_id][index]

    def _batch_row_fields(self, batch: dict, index: int, dataset: Dataset) -> dict:
        fields = {}
        for mapping_field in self.mapping.fields:
            value = batch[mapping_field.source][index]
            field = dataset.field_by_name(mapping_field.target)
            if not field:
                continue

            if field.is_text:
                value = str(value)

            if field.is_image and isinstance(value, Image.Image):
                value = pil_image_to_data_url(value)

            fields[field.name] = value

        return fields

    def _batch_row_metadata(self, batch: dict, index: int, dataset: Dataset) -> dict:
        metadata = {}
        for mapping_metadata in self.mapping.metadata:
            value = batch[mapping_metadata.source][index]
            metadata_property = dataset.metadata_property_by_name(mapping_metadata.target)
            if not metadata_property:
                continue

            metadata[metadata_property.name] = value

        return metadata

    def _batch_row_suggestions(self, batch: dict, index: int, dataset: Dataset) -> list:
        suggestions = []
        for mapping_suggestion in self.mapping.suggestions:
            value = batch[mapping_suggestion.source][index]
            question = dataset.question_by_name(mapping_suggestion.target)
            if not question:
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

    image.save(buffer, format=image.format)

    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:{image.get_format_mimetype()};base64,{base64_image}"
