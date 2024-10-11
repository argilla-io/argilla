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

from datasets import load_dataset
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image

from argilla_server.models.database import Dataset
from argilla_server.search_engine import SearchEngine
from argilla_server.bulk.records_bulk import UpsertRecordsBulk
from argilla_server.api.schemas.v1.records import RecordUpsert as RecordUpsertSchema
from argilla_server.api.schemas.v1.records_bulk import RecordsBulkUpsert as RecordsBulkUpsertSchema

BATCH_SIZE = 100


class HubDataset:
    # TODO: (Ben feedback) rename `name` to `repository_id` or `repo_id`
    # TODO: (Ben feedback) check subset and split and see if we should support None
    def __init__(self, name: str, subset: str, split: str):
        self.dataset = load_dataset(path=name, name=subset, split=split)
        self.iterable_dataset = self.dataset.to_iterable_dataset()

    @property
    def num_rows(self) -> int:
        return self.dataset.num_rows

    def take(self, n: int) -> Self:
        self.iterable_dataset = self.iterable_dataset.take(n)

        return self

    async def import_to(self, db: AsyncSession, search_engine: SearchEngine, dataset: Dataset) -> None:
        if not dataset.is_ready:
            raise Exception("it's not possible to import records to a non published dataset")

        batched_dataset = self.iterable_dataset.batch(batch_size=BATCH_SIZE)
        for batch in batched_dataset:
            await self._import_batch_to(db, search_engine, batch, dataset)

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
            fields=self._batch_row_fields(batch, index, dataset),
            metadata=self._batch_row_metadata(batch, index, dataset),
            external_id=self._batch_row_external_id(batch, index),
            responses=None,
            suggestions=None,
            vectors=None,
        )

    # NOTE: if there is a value with key "id" in the batch, we will use it as external_id
    def _batch_row_external_id(self, batch: dict, index: int) -> Union[str, None]:
        if not "id" in batch:
            return None

        return batch["id"][index]

    def _batch_row_fields(self, batch: dict, index: int, dataset: Dataset) -> dict:
        fields = {}
        for field in dataset.fields:
            value = batch[field.name][index]

            if field.is_text:
                value = str(value)

            if field.is_image and isinstance(value, Image.Image):
                value = pil_image_to_data_url(value)

            fields[field.name] = value

        return fields

    def _batch_row_metadata(self, batch: dict, index: int, dataset: Dataset) -> dict:
        metadata = {}
        for metadata_property in dataset.metadata_properties:
            metadata[metadata_property.name] = batch[metadata_property.name][index]

        return metadata


def pil_image_to_data_url(image: Image.Image):
    buffer = io.BytesIO()

    image.save(buffer, format=image.format)

    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:{image.get_format_mimetype()};base64,{base64_image}"
