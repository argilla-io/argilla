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
from typing import Any, List, Mapping
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.contexts.datasets import get_metadata_property_by_name_and_dataset_id_or_raise
from argilla_server.contexts.questions import get_question_by_name_and_dataset_id_or_raise
from argilla_server.models import Question, Suggestion
from argilla_server.schemas.v1.records import (
    FilterScope,
    MetadataFilterScope,
    RecordFilterScope,
    SearchRecordsQuery,
)
from argilla_server.schemas.v1.responses import ResponseFilterScope
from argilla_server.schemas.v1.suggestions import SuggestionFilterScope


class SearchRecordsQueryValidator:
    def __init__(self, db: AsyncSession, query: SearchRecordsQuery, dataset_id: UUID):
        self._db = db
        self._query = query
        self._dataset_id = dataset_id

    async def validate(self) -> None:
        if self._query.filters:
            for filter in self._query.filters.and_:
                await self._validate_filter_scope(filter.scope)

        if self._query.sort:
            for order in self._query.sort:
                await self._validate_filter_scope(order.scope)

    async def _validate_filter_scope(self, filter_scope: FilterScope) -> None:
        if isinstance(filter_scope, RecordFilterScope):
            return
        elif isinstance(filter_scope, ResponseFilterScope):
            await self._validate_response_filter_scope(filter_scope)
        elif isinstance(filter_scope, SuggestionFilterScope):
            await self._validate_suggestion_filter_scope(filter_scope)
        elif isinstance(filter_scope, MetadataFilterScope):
            await self._validate_metadata_filter_scope(filter_scope)
        else:
            raise ValueError(f"Unknown filter scope entity `{filter_scope.entity}`")

    async def _validate_response_filter_scope(self, filter_scope: ResponseFilterScope) -> None:
        if filter_scope.question is None:
            return

        await get_question_by_name_and_dataset_id_or_raise(self._db, filter_scope.question, self._dataset_id)

    async def _validate_suggestion_filter_scope(self, filter_scope: SuggestionFilterScope) -> None:
        await get_question_by_name_and_dataset_id_or_raise(self._db, filter_scope.question, self._dataset_id)

    async def _validate_metadata_filter_scope(self, filter_scope: MetadataFilterScope) -> None:
        await get_metadata_property_by_name_and_dataset_id_or_raise(
            self._db, filter_scope.metadata_property, self._dataset_id
        )


async def validate_search_records_query(db: AsyncSession, query: SearchRecordsQuery, dataset_id: UUID) -> None:
    await SearchRecordsQueryValidator(db, query, dataset_id).validate()


async def get_dataset_suggestion_agents_by_question(db: AsyncSession, dataset_id: UUID) -> List[Mapping[str, Any]]:
    if db.bind.dialect.name == postgresql.dialect.name:
        return await _get_dataset_suggestion_agents_by_question_postgresql(db, dataset_id)
    else:
        return await _get_dataset_suggestion_agents_by_question_sqlite(db, dataset_id)


async def _get_dataset_suggestion_agents_by_question_postgresql(
    db: AsyncSession, dataset_id: UUID
) -> List[Mapping[str, Any]]:
    result = await db.execute(
        select(
            Question.id.label("question_id"),
            Question.name.label("question_name"),
            func.array_remove(func.array_agg(Suggestion.agent.distinct()), None).label("suggestion_agents"),
        )
        .outerjoin(Suggestion)
        .where(Question.dataset_id == dataset_id)
        .group_by(Question.id)
        .order_by(Question.inserted_at)
    )

    return result.mappings().all()


async def _get_dataset_suggestion_agents_by_question_sqlite(
    db: AsyncSession, dataset_id: UUID
) -> List[Mapping[str, Any]]:
    result = await db.execute(
        select(
            Question.id.label("question_id"),
            Question.name.label("question_name"),
            func.group_concat(Suggestion.agent.distinct()).label("suggestion_agents"),
        )
        .outerjoin(Suggestion)
        .where(Question.dataset_id == dataset_id)
        .group_by(Question.id)
        .order_by(Question.inserted_at)
    )

    rows = result.mappings().all()

    return [
        {
            "question_id": row["question_id"],
            "question_name": row["question_name"],
            "suggestion_agents": row["suggestion_agents"].split(",") if row["suggestion_agents"] else [],
        }
        for row in rows
    ]
