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
from typing import Dict, List, Sequence, Tuple, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from argilla_server.api.schemas.v1.records import RecordCreate, RecordUpsert
from argilla_server.api.schemas.v1.records_bulk import (
    RecordsBulk,
    RecordsBulkCreate,
    RecordsBulkUpsert,
    RecordsBulkWithUpdateInfo,
)
from argilla_server.api.schemas.v1.responses import UserResponseCreate
from argilla_server.api.schemas.v1.suggestions import SuggestionCreate
from argilla_server.contexts import distribution
from argilla_server.contexts.records import (
    fetch_records_by_external_ids_as_dict,
    fetch_records_by_ids_as_dict,
)
from argilla_server.models import Dataset, Record, Response, Suggestion, Vector, VectorSettings
from argilla_server.search_engine import SearchEngine
from argilla_server.validators.records import RecordsBulkCreateValidator, RecordsBulkUpsertValidator


class CreateRecordsBulk:
    def __init__(self, db: AsyncSession, search_engine: SearchEngine):
        self._db = db
        self._search_engine = search_engine

    async def create_records_bulk(self, dataset: Dataset, bulk_create: RecordsBulkCreate) -> RecordsBulk:
        await RecordsBulkCreateValidator.validate(self._db, bulk_create, dataset)

        async with self._db.begin_nested():
            records = [
                Record(
                    fields=jsonable_encoder(record_create.fields),
                    metadata_=record_create.metadata,
                    external_id=record_create.external_id,
                    dataset_id=dataset.id,
                )
                for record_create in bulk_create.items
            ]

            self._db.add_all(records)
            await self._db.flush(records)

            await self._upsert_records_relationships(records, bulk_create.items)
            await _preload_records_relationships_before_index(self._db, records)
            await distribution.unsafe_update_records_status(self._db, records)
            await self._search_engine.index_records(dataset, records)

        await self._db.commit()

        return RecordsBulk(items=records)

    async def _upsert_records_relationships(self, records: List[Record], records_create: List[RecordCreate]) -> None:
        records_and_suggestions = list(zip(records, [r.suggestions for r in records_create]))
        records_and_responses = list(zip(records, [r.responses for r in records_create]))
        records_and_vectors = list(zip(records, [r.vectors for r in records_create]))
        # The asyncio.gather version is replaced by the following three await calls to avoid the following error:
        # https://github.com/sqlalchemy/sqlalchemy/discussions/9312

        await self._upsert_records_suggestions(records_and_suggestions)
        await self._upsert_records_vectors(records_and_vectors)
        await self._upsert_records_responses(records_and_responses)

    async def _upsert_records_suggestions(
        self, records_and_suggestions: List[Tuple[Record, List[SuggestionCreate]]]
    ) -> List[Suggestion]:
        upsert_many_suggestions = []
        for idx, (record, suggestions) in enumerate(records_and_suggestions):
            for suggestion_create in suggestions or []:
                upsert_many_suggestions.append(dict(**suggestion_create.dict(), record_id=record.id))

        if not upsert_many_suggestions:
            return []

        return await Suggestion.upsert_many(
            self._db,
            objects=upsert_many_suggestions,
            constraints=[Suggestion.record_id, Suggestion.question_id],
            autocommit=False,
        )

    async def _upsert_records_responses(
        self, records_and_responses: List[Tuple[Record, List[UserResponseCreate]]]
    ) -> List[Response]:
        upsert_many_responses = []
        for idx, (record, responses) in enumerate(records_and_responses):
            for response_create in responses or []:
                upsert_many_responses.append(dict(**response_create.dict(), record_id=record.id))

        if not upsert_many_responses:
            return []

        return await Response.upsert_many(
            self._db,
            objects=upsert_many_responses,
            constraints=[Response.record_id, Response.user_id],
            autocommit=False,
        )

    async def _upsert_records_vectors(
        self, records_and_vectors: List[Tuple[Record, Dict[str, List[float]]]]
    ) -> List[Vector]:
        upsert_many_vectors = []
        for idx, (record, vectors) in enumerate(records_and_vectors):
            dataset = record.dataset

            for name, value in (vectors or {}).items():
                settings = dataset.vector_settings_by_name(name)
                upsert_many_vectors.append(dict(value=value, record_id=record.id, vector_settings_id=settings.id))

        if not upsert_many_vectors:
            return []

        return await Vector.upsert_many(
            self._db,
            objects=upsert_many_vectors,
            constraints=[Vector.record_id, Vector.vector_settings_id],
            autocommit=False,
        )

    def _metadata_is_set(self, record_create: RecordCreate) -> bool:
        return "metadata" in record_create.__fields_set__


class UpsertRecordsBulk(CreateRecordsBulk):
    async def upsert_records_bulk(self, dataset: Dataset, bulk_upsert: RecordsBulkUpsert) -> RecordsBulkWithUpdateInfo:
        found_records = await self._fetch_existing_dataset_records(dataset, bulk_upsert.items)
        # found_records is passed to the validator to avoid querying the database again, but ideally, it should be
        # computed inside the validator
        await RecordsBulkUpsertValidator.validate(bulk_upsert, dataset, found_records)

        records = []
        async with self._db.begin_nested():
            for record_upsert in bulk_upsert.items:
                record = found_records.get(record_upsert.id) or found_records.get(record_upsert.external_id)
                if not record:
                    record = Record(
                        fields=jsonable_encoder(record_upsert.fields),
                        metadata_=record_upsert.metadata,
                        external_id=record_upsert.external_id,
                        dataset_id=dataset.id,
                    )
                elif self._metadata_is_set(record_upsert):
                    record.metadata_ = record_upsert.metadata
                    record.updated_at = datetime.utcnow()

                records.append(record)

            self._db.add_all(records)
            await self._db.flush(records)

            await self._upsert_records_relationships(records, bulk_upsert.items)
            await _preload_records_relationships_before_index(self._db, records)
            await distribution.unsafe_update_records_status(self._db, records)
            await self._search_engine.index_records(dataset, records)

        await self._db.commit()

        return RecordsBulkWithUpdateInfo(
            items=records,
            updated_item_ids=[record.id for record in found_records.values()],
        )

    async def _fetch_existing_dataset_records(
        self,
        dataset: Dataset,
        records_upsert: List[RecordUpsert],
    ) -> Dict[Union[str, UUID], Record]:
        records_by_external_id = await fetch_records_by_external_ids_as_dict(
            self._db, dataset, [r.external_id for r in records_upsert]
        )
        records_by_id = await fetch_records_by_ids_as_dict(
            self._db, dataset, [r.id for r in records_upsert if r.id not in records_by_external_id]
        )

        return {**records_by_external_id, **records_by_id}


async def _preload_records_relationships_before_index(db: "AsyncSession", records: Sequence[Record]) -> None:
    await db.execute(
        select(Record)
        .filter(Record.id.in_([record.id for record in records]))
        .options(
            selectinload(Record.responses).selectinload(Response.user),
            selectinload(Record.responses_submitted),
            selectinload(Record.suggestions).selectinload(Suggestion.question),
            selectinload(Record.vectors),
        )
    )
