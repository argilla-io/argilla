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

from typing import Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import argilla_server.errors.future as errors
from argilla_server.models import Dataset, Question, User
from argilla_server.policies import QuestionPolicyV1, authorize
from argilla_server.schemas.v1.questions import (
    QuestionCreate,
    QuestionUpdate,
)
from argilla_server.validators.questions import (
    QuestionCreateValidator,
    QuestionDeleteValidator,
    QuestionUpdateValidator,
)


async def get_question_by_id(db: AsyncSession, question_id: UUID) -> Union[Question, None]:
    return (
        await db.execute(select(Question).filter_by(id=question_id).options(selectinload(Question.dataset)))
    ).scalar_one_or_none()


async def get_question_by_name_and_dataset_id(db: AsyncSession, name: str, dataset_id: UUID) -> Union[Question, None]:
    return (await db.execute(select(Question).filter_by(name=name, dataset_id=dataset_id))).scalar_one_or_none()


async def get_question_by_name_and_dataset_id_or_raise(db: AsyncSession, name: str, dataset_id: UUID) -> Question:
    question = await get_question_by_name_and_dataset_id(db, name, dataset_id)
    if question is None:
        raise errors.NotFoundError(f"Question with name `{name}` not found for dataset with id `{dataset_id}`")

    return question


async def create_question(db: AsyncSession, dataset: Dataset, question_create: QuestionCreate) -> Question:
    QuestionCreateValidator(question_create).validate_for(dataset)

    return await Question.create(
        db,
        name=question_create.name,
        title=question_create.title,
        description=question_create.description,
        required=question_create.required,
        settings=question_create.settings.dict(),
        dataset_id=dataset.id,
    )


async def update_question(
    db: AsyncSession, question_id: UUID, question_update: QuestionUpdate, current_user: User
) -> Question:
    question = await get_question_by_id(db, question_id)
    if not question:
        raise errors.NotFoundError()

    await authorize(current_user, QuestionPolicyV1.update(question))

    QuestionUpdateValidator(question_update).validate_for(question)

    params = question_update.dict(exclude_unset=True)

    return await question.update(db, **params)


async def delete_question(db: AsyncSession, question: Question) -> Question:
    QuestionDeleteValidator().validate_for(question.dataset)

    return await question.delete(db)
