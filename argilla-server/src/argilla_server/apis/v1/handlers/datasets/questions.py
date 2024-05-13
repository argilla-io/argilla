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

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from argilla_server.apis.v1.handlers.datasets.datasets import _get_dataset_or_raise
from argilla_server.contexts import questions
from argilla_server.database import get_async_db
from argilla_server.models import User
from argilla_server.policies import DatasetPolicyV1, authorize
from argilla_server.schemas.v1.questions import Question, QuestionCreate, Questions
from argilla_server.security import auth

router = APIRouter()


@router.get("/datasets/{dataset_id}/questions", response_model=Questions)
async def list_dataset_questions(
    *, db: AsyncSession = Depends(get_async_db), dataset_id: UUID, current_user: User = Security(auth.get_current_user)
):
    dataset = await _get_dataset_or_raise(db, dataset_id, with_questions=True)

    await authorize(current_user, DatasetPolicyV1.get(dataset))

    return Questions(items=dataset.questions)


@router.post("/datasets/{dataset_id}/questions", status_code=status.HTTP_201_CREATED, response_model=Question)
async def create_dataset_question(
    *,
    db: AsyncSession = Depends(get_async_db),
    dataset_id: UUID,
    question_create: QuestionCreate,
    current_user: User = Security(auth.get_current_user),
):
    # TODO: Review this flow since we're putting logic here that will be used internally by the context
    #  Fields and questions are required to apply validations.
    dataset = await _get_dataset_or_raise(db, dataset_id, with_fields=True, with_questions=True)

    await authorize(current_user, DatasetPolicyV1.create_question(dataset))

    if await questions.get_question_by_name_and_dataset_id(db, question_create.name, dataset_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Question with name `{question_create.name}` already exists for dataset with id `{dataset_id}`",
        )

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        return await questions.create_question(db, dataset, question_create)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
