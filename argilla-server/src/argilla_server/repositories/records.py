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

from typing import Union, List, Tuple, Sequence, Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, contains_eager

from argilla_server.database import get_async_db
from argilla_server.models import Record, VectorSettings, Vector, Response


class RecordsRepository:
    def __init__(
        self,
        db: AsyncSession = Depends(get_async_db),
    ):
        self.db = db

    async def list_by_dataset_id(
        self,
        dataset_id: UUID,
        offset: int,
        limit: int,
        with_responses: bool = False,
        with_suggestions: bool = False,
        with_vectors: Union[bool, List[str]] = False,
    ) -> Tuple[Sequence[Record], int]:
        query = select(Record).filter_by(dataset_id=dataset_id)
        query = await self._configure_record_load_relationships(dataset_id, query, with_suggestions, with_vectors)

        if with_responses:
            query = query.options(selectinload(Record.responses))

        records = (await self.db.scalars(query.offset(offset).limit(limit).order_by(Record.inserted_at))).unique().all()
        total = await self.db.scalar(select(func.count(Record.id)).filter_by(dataset_id=dataset_id))

        return records, total

    async def list_by_dataset_id_and_ids(
        self,
        dataset_id: UUID,
        ids: List[UUID],
        user_id: Optional[UUID] = None,
        with_responses: bool = False,
        with_suggestions: bool = False,
        with_vectors: Union[bool, List[str]] = False,
    ):
        query = select(Record).filter_by(dataset_id=dataset_id).filter(Record.id.in_(ids))
        query = await self._configure_record_load_relationships(dataset_id, query, with_suggestions, with_vectors)

        if with_responses:
            if user_id:
                query = query.outerjoin(
                    Response, and_(Response.record_id == Record.id, Response.user_id == user_id)
                ).options(contains_eager(Record.responses))
            else:
                query = query.options(selectinload(Record.responses))

        return (await self.db.scalars(query)).unique().all()

    async def _configure_record_load_relationships(self, dataset_id, query, with_suggestions, with_vectors):
        if with_suggestions:
            query = query.options(selectinload(Record.suggestions))

        if with_vectors is True:
            query = query.options(selectinload(Record.vectors))
        elif isinstance(with_vectors, list):
            subquery = select(VectorSettings.id).filter(
                and_(VectorSettings.dataset_id == dataset_id, VectorSettings.name.in_(with_vectors))
            )
            query = query.outerjoin(
                Vector, and_(Vector.record_id == Record.id, Vector.vector_settings_id.in_(subquery))
            ).options(contains_eager(Record.vectors))

        return query
