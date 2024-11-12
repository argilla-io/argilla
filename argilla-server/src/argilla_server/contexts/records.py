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

from typing import Dict, Sequence, Union, List, Tuple, Optional
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, and_, func, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, contains_eager

from argilla_server.api.schemas.v1.records import RecordUpdate
from argilla_server.api.schemas.v1.vectors import Vector as VectorSchema

from argilla_server.models import Dataset, Record, VectorSettings, Vector, Response, Suggestion
from argilla_server.search_engine import SearchEngine
from argilla_server.validators.records import RecordUpdateValidator


async def list_dataset_records(
    db: AsyncSession,
    dataset_id: UUID,
    offset: int,
    limit: int,
    with_responses: bool = False,
    with_suggestions: bool = False,
    with_vectors: Union[bool, List[str]] = False,
) -> Tuple[Sequence[Record], int]:
    query = _build_list_records_query(
        dataset_id=dataset_id,
        offset=offset,
        limit=limit,
        with_responses=with_responses,
        with_suggestions=with_suggestions,
        with_vectors=with_vectors,
    )

    records = (await db.scalars(query)).unique().all()
    total = await db.scalar(select(func.count(Record.id)).filter_by(dataset_id=dataset_id))

    return records, total


async def list_dataset_records_by_ids(
    db: AsyncSession, dataset_id: UUID, record_ids: Sequence[UUID]
) -> Sequence[Record]:
    query = select(Record).where(and_(Record.id.in_(record_ids), Record.dataset_id == dataset_id))
    return (await db.scalars(query)).unique().all()


async def list_dataset_records_by_external_ids(
    db: AsyncSession, dataset_id: UUID, external_ids: Sequence[str]
) -> Sequence[Record]:
    query = (
        select(Record)
        .where(and_(Record.external_id.in_(external_ids), Record.dataset_id == dataset_id))
        .options(selectinload(Record.dataset))
    )

    return (await db.scalars(query)).unique().all()


async def fetch_records_by_ids_as_dict(
    db: AsyncSession, dataset: Dataset, record_ids: Sequence[UUID]
) -> Dict[UUID, Record]:
    records_by_ids = await list_dataset_records_by_ids(db, dataset.id, record_ids)
    return {record.id: record for record in records_by_ids}


async def fetch_records_by_external_ids_as_dict(
    db: AsyncSession, dataset: Dataset, external_ids: Sequence[str]
) -> Dict[str, Record]:
    records_by_external_ids = await list_dataset_records_by_external_ids(db, dataset.id, external_ids)
    return {record.external_id: record for record in records_by_external_ids}


def _build_list_records_query(
    dataset_id,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    with_responses: bool = False,
    with_suggestions: bool = False,
    with_vectors: Union[bool, List[str]] = False,
) -> Select:
    query = select(Record).filter_by(dataset_id=dataset_id)

    if with_responses:
        query = query.options(selectinload(Record.responses))

    if with_suggestions:
        query = query.options(selectinload(Record.suggestions))

    if with_vectors is True:
        query = query.options(selectinload(Record.vectors).selectinload(Vector.vector_settings))
    elif isinstance(with_vectors, list):
        subquery = select(VectorSettings.id).filter(
            and_(VectorSettings.dataset_id == dataset_id, VectorSettings.name.in_(with_vectors))
        )
        query = query.outerjoin(
            Vector, and_(Vector.record_id == Record.id, Vector.vector_settings_id.in_(subquery))
        ).options(contains_eager(Record.vectors).selectinload(Vector.vector_settings))

    if offset is not None:
        query = query.offset(offset)

    if limit is not None:
        query = query.limit(limit)

    return query.order_by(Record.inserted_at)


async def _preload_record_relationships_before_index(db: AsyncSession, record: Record) -> None:
    await db.execute(
        select(Record)
        .filter_by(id=record.id)
        .options(
            selectinload(Record.responses).selectinload(Response.user),
            selectinload(Record.suggestions).selectinload(Suggestion.question),
            selectinload(Record.vectors),
        )
    )


async def update_record(
    db: AsyncSession, search_engine: "SearchEngine", record: Record, record_update: "RecordUpdate"
) -> Record:
    if not record_update.has_changes():
        return record

    dataset = record.dataset

    await RecordUpdateValidator.validate(record_update, dataset, record)

    if record_update.is_set("metadata"):
        record.metadata_ = record_update.metadata

    if record_update.is_set("suggestions"):
        # Delete all suggestions and replace them with the new ones
        await Suggestion.delete_many(db, [Suggestion.record_id == record.id], autocommit=False)
        await db.refresh(record, attribute_names=["suggestions"])

        record.suggestions = [
            Suggestion(
                type=suggestion.type,
                score=suggestion.score,
                value=jsonable_encoder(suggestion.value),
                agent=suggestion.agent,
                question_id=suggestion.question_id,
                record_id=record.id,
            )
            for suggestion in record_update.suggestions
        ]

    await record.save(db, autocommit=False)

    if record_update.vectors:
        await Vector.upsert_many(
            db,
            objects=[
                VectorSchema(
                    record_id=record.id,
                    vector_settings_id=dataset.vector_settings_by_name(name).id,
                    value=value,
                )
                for name, value in record_update.vectors.items()
            ],
            constraints=[Vector.record_id, Vector.vector_settings_id],
        )
        await db.refresh(record, attribute_names=["vectors"])

    await db.commit()

    await _preload_record_relationships_before_index(db, record)
    await search_engine.index_records(record.dataset, [record])

    return record


async def delete_record(db: AsyncSession, search_engine: "SearchEngine", record: Record) -> Record:
    record = await record.delete(db=db, autocommit=True)

    await search_engine.delete_records(dataset=record.dataset, records=[record])

    return record


async def delete_records(
    db: AsyncSession, search_engine: "SearchEngine", dataset: Dataset, records_ids: List[UUID]
) -> None:
    records = await Record.delete_many(
        db=db,
        conditions=[Record.id.in_(records_ids), Record.dataset_id == dataset.id],
        autocommit=True,
    )

    await search_engine.delete_records(dataset=dataset, records=records)
