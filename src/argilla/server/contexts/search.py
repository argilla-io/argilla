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
from typing import Mapping, List, Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession

from argilla.server.models import Question, Suggestion


async def get_dataset_suggestion_agents_by_question(db: AsyncSession, dataset_id: UUID) -> List[Mapping[str, Any]]:
    if db.bind.dialect.name == postgresql.dialect.name:
        return await _get_dataset_suggestion_agents_by_question_postgresql(db, dataset_id)
    else:
        return await _get_dataset_suggestion_agents_by_question_sqlite(db, dataset_id)


async def _get_dataset_suggestion_agents_by_question_postgresql(db: AsyncSession, dataset_id: UUID) -> List[Mapping[str, Any]]:
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


async def _get_dataset_suggestion_agents_by_question_sqlite(db: AsyncSession, dataset_id: UUID) -> List[Mapping[str, Any]]:
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
