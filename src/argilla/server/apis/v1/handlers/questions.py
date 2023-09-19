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

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from argilla.server.contexts import datasets
from argilla.server.database import get_async_db
from argilla.server.models import Question, User
from argilla.server.policies import QuestionPolicyV1, authorize
from argilla.server.schemas.v1.questions import Question as QuestionSchema
from argilla.server.schemas.v1.questions import (
    QuestionUpdate,
)
from argilla.server.security import auth

router = APIRouter(tags=["questions"])


async def _get_question(db: "AsyncSession", question_id: UUID) -> Question:
    question = await datasets.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id `{question_id}` not found",
        )
    return question


@router.patch("/questions/{question_id}", response_model=QuestionSchema)
async def update_question(
    *,
    db: AsyncSession = Depends(get_async_db),
    question_id: UUID,
    question_update: QuestionUpdate,
    current_user: User = Security(auth.get_current_user),
):
    question = await _get_question(db, question_id)

    await authorize(current_user, QuestionPolicyV1.update(question))

    if question_update.settings and question_update.settings.type != question.settings["type"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Question type cannot be changed. Expected '{question.settings['type']}' but got '{question_update.settings.type}'",
        )

    return await datasets.update_question(db, question, question_update)


@router.delete("/questions/{question_id}", response_model=QuestionSchema)
async def delete_question(
    *, db: AsyncSession = Depends(get_async_db), question_id: UUID, current_user: User = Security(auth.get_current_user)
):
    question = await _get_question(db, question_id)

    await authorize(current_user, QuestionPolicyV1.delete(question))

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        await datasets.delete_question(db, question)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))

    return question
