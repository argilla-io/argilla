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
from starlette import status

from argilla_server.api.policies.v1 import DatasetPolicy, authorize
from argilla_server.api.schemas.v1.questions import Question, QuestionCreate, Questions
from argilla_server.contexts import questions
from argilla_server.database import get_async_db
from argilla_server.models import Dataset, User
from argilla_server.security import auth
from argilla_server.telemetry import TelemetryClient, get_telemetry_client

router = APIRouter()


@router.get("/datasets/{dataset_id}/questions", response_model=Questions)
async def list_dataset_questions(
    *, db: AsyncSession = Depends(get_async_db), dataset_id: UUID, current_user: User = Security(auth.get_current_user)
):
    dataset = await Dataset.get_or_raise(db, dataset_id, options=[selectinload(Dataset.questions)])

    await authorize(current_user, DatasetPolicy.get(dataset))

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
    dataset = await Dataset.get_or_raise(
        db,
        dataset_id,
        options=[
            selectinload(Dataset.fields),
            selectinload(Dataset.questions),
        ],
    )

    await authorize(current_user, DatasetPolicy.create_question(dataset))

    return await questions.create_question(db, dataset, question_create)
