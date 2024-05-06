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

from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi import Response as HTTPResponse
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.contexts import datasets, questions
from argilla_server.database import get_async_db
from argilla_server.models import Record, User
from argilla_server.policies import RecordPolicyV1, authorize
from argilla_server.schemas.v1.records import Record as RecordSchema
from argilla_server.schemas.v1.records import RecordUpdate
from argilla_server.schemas.v1.responses import Response, ResponseCreate
from argilla_server.schemas.v1.suggestions import Suggestion, SuggestionCreate, Suggestions
from argilla_server.search_engine import SearchEngine, get_search_engine
from argilla_server.security import auth
from argilla_server.utils import parse_uuids

DELETE_RECORD_SUGGESTIONS_LIMIT = 100

router = APIRouter(tags=["records"])


async def _get_record(
    db: AsyncSession,
    record_id: UUID,
    with_dataset: bool = False,
    with_suggestions: bool = False,
    with_vectors: bool = False,
) -> Record:
    record = await datasets.get_record_by_id(db, record_id, with_dataset, with_suggestions, with_vectors)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with id `{record_id}` not found",
        )
    return record


@router.get("/records/{record_id}", response_model=RecordSchema)
async def get_record(
    *,
    db: AsyncSession = Depends(get_async_db),
    record_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    record = await _get_record(db, record_id, with_dataset=True, with_suggestions=True)

    await authorize(current_user, RecordPolicyV1.get(record))

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
    record = await _get_record(db, record_id, with_dataset=True, with_suggestions=True, with_vectors=True)

    await authorize(current_user, RecordPolicyV1.update(record))

    try:
        return await datasets.update_record(db, search_engine, record, record_update)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.post("/records/{record_id}/responses", status_code=status.HTTP_201_CREATED, response_model=Response)
async def create_record_response(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    record_id: UUID,
    response_create: ResponseCreate,
    current_user: User = Security(auth.get_current_user),
):
    record = await _get_record(db, record_id, with_dataset=True)

    await authorize(current_user, RecordPolicyV1.create_response(record))

    if await datasets.get_response_by_record_id_and_user_id(db, record_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Response already exists for record with id `{record_id}` and by user with id `{current_user.id}`",
        )

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        return await datasets.create_response(db, search_engine, record, current_user, response_create)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.get("/records/{record_id}/suggestions", status_code=status.HTTP_200_OK, response_model=Suggestions)
async def get_record_suggestions(
    *, db: AsyncSession = Depends(get_async_db), record_id: UUID, current_user: User = Security(auth.get_current_user)
):
    record = await _get_record(db, record_id, with_dataset=True, with_suggestions=True)

    await authorize(current_user, RecordPolicyV1.get_suggestions(record))

    return Suggestions(items=record.suggestions)


@router.put(
    "/records/{record_id}/suggestions",
    summary="Create or update a suggestion",
    responses={
        status.HTTP_200_OK: {"model": Suggestion, "description": "Suggestion updated"},
        status.HTTP_201_CREATED: {"model": Suggestion, "description": "Suggestion created"},
    },
    status_code=status.HTTP_201_CREATED,
    response_model=Suggestion,
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
    record = await _get_record(db, record_id, with_dataset=True)

    await authorize(current_user, RecordPolicyV1.create_suggestion(record))

    question = await questions.get_question_by_id(db, suggestion_create.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Question with id `{suggestion_create.question_id}` not found",
        )

    if await datasets.get_suggestion_by_record_id_and_question_id(db, record_id, suggestion_create.question_id):
        # There is already a suggestion for this record and question, so we update it.
        response.status_code = status.HTTP_200_OK

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        return await datasets.upsert_suggestion(db, search_engine, record, question, suggestion_create)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


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
    record = await _get_record(db, record_id, with_dataset=True)

    await authorize(current_user, RecordPolicyV1.delete_suggestions(record))

    suggestion_ids = parse_uuids(ids)
    num_suggestions = len(suggestion_ids)

    if num_suggestions == 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No suggestions IDs provided")

    if num_suggestions > DELETE_RECORD_SUGGESTIONS_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot delete more than {DELETE_RECORD_SUGGESTIONS_LIMIT} suggestions at once",
        )

    await datasets.delete_suggestions(db, search_engine, record, suggestion_ids)


@router.delete("/records/{record_id}", response_model=RecordSchema, response_model_exclude_unset=True)
async def delete_record(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    record_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    record = await _get_record(db, record_id, with_dataset=True)

    await authorize(current_user, RecordPolicyV1.delete(record))

    return await datasets.delete_record(db, search_engine, record)
