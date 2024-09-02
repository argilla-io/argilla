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

from uuid import UUID

from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from argilla_server.api.policies.v1 import QuestionPolicy, authorize
from argilla_server.api.schemas.v1.questions import Question as QuestionSchema
from argilla_server.api.schemas.v1.questions import QuestionUpdate
from argilla_server.contexts import questions
from argilla_server.database import get_async_db
from argilla_server.models import Question, User
from argilla_server.security import auth

router = APIRouter(tags=["questions"])


@router.patch("/questions/{question_id}", response_model=QuestionSchema)
async def update_question(
    *,
    db: AsyncSession = Depends(get_async_db),
    question_id: UUID,
    question_update: QuestionUpdate,
    current_user: User = Security(auth.get_current_user),
):
    question = await Question.get_or_raise(db, question_id, options=[selectinload(Question.dataset)])

    await authorize(current_user, QuestionPolicy.update(question))

    return await questions.update_question(db, question, question_update)


@router.delete("/questions/{question_id}", response_model=QuestionSchema)
async def delete_question(
    *,
    db: AsyncSession = Depends(get_async_db),
    question_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    question = await Question.get_or_raise(db, question_id, options=[selectinload(Question.dataset)])

    await authorize(current_user, QuestionPolicy.delete(question))

    return await questions.delete_question(db, question)
