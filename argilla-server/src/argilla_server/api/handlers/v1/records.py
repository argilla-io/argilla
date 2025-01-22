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

from fastapi import APIRouter, Depends, Query, Security, status
from fastapi import Response as HTTPResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from argilla_server.api.policies.v1 import RecordPolicy, authorize
from argilla_server.api.schemas.v1.records import Record as RecordSchema
from argilla_server.api.schemas.v1.records import RecordUpdate
from argilla_server.api.schemas.v1.responses import Response, ResponseCreate
from argilla_server.api.schemas.v1.suggestions import Suggestion as SuggestionSchema
from argilla_server.api.schemas.v1.suggestions import SuggestionCreate, Suggestions
from argilla_server.contexts import datasets, records
from argilla_server.database import get_async_db
from argilla_server.errors.future.base_errors import NotFoundError, UnprocessableEntityError
from argilla_server.models import Dataset, Question, Record, Suggestion, User
from argilla_server.search_engine import SearchEngine, get_search_engine
from argilla_server.security import auth
from argilla_server.utils import parse_uuids

DELETE_RECORD_SUGGESTIONS_LIMIT = 100

router = APIRouter(tags=["records"])


@router.get("/records/{record_id}", response_model=RecordSchema)
async def get_record(
    *,
    db: AsyncSession = Depends(get_async_db),
    record_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    record = await Record.get_or_raise(
        db,
        record_id,
        options=[
            selectinload(Record.dataset),
            selectinload(Record.suggestions),
            selectinload(Record.responses),
            selectinload(Record.vectors),
        ],
    )

    await authorize(current_user, RecordPolicy.get(record))

    return record


@router.patch("/records/{record_id}", status_code=status.HTTP_200_OK, response_model=RecordSchema)
async def update_record(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    record_id: UUID,
    record_update: RecordUpdate,
    current_user: User = Security(auth.get_current_user),
):
    record = await Record.get_or_raise(
        db,
        record_id,
        options=[
            selectinload(Record.dataset).options(
                selectinload(Dataset.questions),
                selectinload(Dataset.metadata_properties),
                selectinload(Dataset.vectors_settings),
                selectinload(Dataset.fields),
            ),
            selectinload(Record.suggestions),
            selectinload(Record.responses),
            selectinload(Record.vectors),
        ],
    )

    await authorize(current_user, RecordPolicy.update(record))

    return await records.update_record(db, search_engine, record, record_update)


@router.post("/records/{record_id}/responses", status_code=status.HTTP_201_CREATED, response_model=Response)
async def create_record_response(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    record_id: UUID,
    response_create: ResponseCreate,
    current_user: User = Security(auth.get_current_user),
):
    record = await Record.get_or_raise(
        db,
        record_id,
        options=[
            selectinload(Record.dataset).selectinload(Dataset.questions),
            selectinload(Record.dataset).selectinload(Dataset.metadata_properties),
        ],
    )

    await authorize(current_user, RecordPolicy.create_response(record))

    return await datasets.create_response(db, search_engine, record, current_user, response_create)


@router.get("/records/{record_id}/suggestions", status_code=status.HTTP_200_OK, response_model=Suggestions)
async def get_record_suggestions(
    *,
    db: AsyncSession = Depends(get_async_db),
    record_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    record = await Record.get_or_raise(
        db,
        record_id,
        options=[
            selectinload(Record.dataset).selectinload(Dataset.questions),
            selectinload(Record.dataset).selectinload(Dataset.metadata_properties),
            selectinload(Record.suggestions),
        ],
    )

    await authorize(current_user, RecordPolicy.get_suggestions(record))

    return Suggestions(items=record.suggestions)


@router.put(
    "/records/{record_id}/suggestions",
    summary="Create or update a suggestion",
    responses={
        status.HTTP_200_OK: {"model": SuggestionSchema, "description": "Suggestion updated"},
        status.HTTP_201_CREATED: {"model": SuggestionSchema, "description": "Suggestion created"},
    },
    status_code=status.HTTP_201_CREATED,
    response_model=SuggestionSchema,
)
async def upsert_suggestion(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    record_id: UUID,
    suggestion_create: SuggestionCreate,
    current_user: User = Security(auth.get_current_user),
    response: HTTPResponse,
):
    record = await Record.get_or_raise(
        db,
        record_id,
        options=[
            selectinload(Record.dataset).selectinload(Dataset.questions),
            selectinload(Record.dataset).selectinload(Dataset.metadata_properties),
        ],
    )

    await authorize(current_user, RecordPolicy.create_suggestion(record))

    try:
        question = await Question.get_or_raise(
            db,
            suggestion_create.question_id,
            options=[selectinload(Question.dataset)],
        )
    except NotFoundError as e:
        raise UnprocessableEntityError(e.message)

    # NOTE: If there is already a suggestion for this record and question, we update it instead of creating a new one.
    # So we set the correct status code here.
    if await Suggestion.get_by(db, record_id=record_id, question_id=suggestion_create.question_id):
        response.status_code = status.HTTP_200_OK

    return await datasets.upsert_suggestion(db, search_engine, record, question, suggestion_create)


@router.delete(
    "/records/{record_id}/suggestions",
    summary="Delete suggestions for a record",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_record_suggestions(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    record_id: UUID,
    current_user: User = Security(auth.get_current_user),
    ids: str = Query(..., description="A comma separated list with the IDs of the suggestions to be removed"),
):
    record = await Record.get_or_raise(
        db,
        record_id,
        options=[
            selectinload(Record.dataset).selectinload(Dataset.questions),
            selectinload(Record.dataset).selectinload(Dataset.metadata_properties),
        ],
    )

    await authorize(current_user, RecordPolicy.delete_suggestions(record))

    suggestion_ids = parse_uuids(ids)
    num_suggestions = len(suggestion_ids)

    if num_suggestions == 0:
        raise UnprocessableEntityError("No suggestions IDs provided")

    if num_suggestions > DELETE_RECORD_SUGGESTIONS_LIMIT:
        raise UnprocessableEntityError(f"Cannot delete more than {DELETE_RECORD_SUGGESTIONS_LIMIT} suggestions at once")

    await datasets.delete_suggestions(db, search_engine, record, suggestion_ids)


@router.delete("/records/{record_id}", response_model=RecordSchema, response_model_exclude_unset=True)
async def delete_record(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    record_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    record = await Record.get_or_raise(
        db,
        record_id,
        options=[
            selectinload(Record.dataset).selectinload(Dataset.questions),
            selectinload(Record.dataset).selectinload(Dataset.metadata_properties),
        ],
    )

    await authorize(current_user, RecordPolicy.delete(record))

    return await records.delete_record(db, search_engine, record)
