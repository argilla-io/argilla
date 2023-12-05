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

import argilla.server.errors.future as errors
from argilla.server.contexts import datasets
from argilla.server.database import get_async_db
from argilla.server.models import Record, Response, User
from argilla.server.policies import RecordPolicyV1, ResponsePolicyV1, authorize
from argilla.server.schemas.v1.responses import (
    Response as ResponseSchema,
)
from argilla.server.schemas.v1.responses import (
    ResponseBulk,
    ResponseBulkError,
    ResponsesBulk,
    ResponsesBulkCreate,
    ResponseUpdate,
)
from argilla.server.search_engine import SearchEngine, get_search_engine
from argilla.server.security import auth

router = APIRouter(tags=["responses"])


async def _get_response(db: AsyncSession, response_id: UUID) -> Response:
    response = await datasets.get_response_by_id(db, response_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Response with id `{response_id}` not found",
        )

    return response


async def _get_record(db: AsyncSession, record_id: UUID) -> Record:
    record = await datasets.get_record_by_id(db, record_id, with_dataset=True)
    if record is None:
        raise errors.NotFoundError(f"Record with id `{record_id}` not found")

    return record


@router.post("/me/responses/bulk", response_model=ResponsesBulk)
async def create_current_user_responses_bulk(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    body: ResponsesBulkCreate,
    current_user: User = Security(auth.get_current_user),
):
    responses_bulk_items = []
    for item in body.items:
        try:
            record = await _get_record(db, item.record_id)

            await authorize(current_user, RecordPolicyV1.create_response(record))

            response = await datasets.upsert_response(db, search_engine, record, current_user, item)
        except Exception as err:
            responses_bulk_items.append(ResponseBulk(item=None, error=ResponseBulkError(detail=str(err))))
        else:
            responses_bulk_items.append(ResponseBulk(item=ResponseSchema.from_orm(response), error=None))

    return ResponsesBulk(items=responses_bulk_items)


@router.put("/responses/{response_id}", response_model=ResponseSchema)
async def update_response(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    response_id: UUID,
    response_update: ResponseUpdate,
    current_user: User = Security(auth.get_current_user),
):
    response = await _get_response(db, response_id)

    await authorize(current_user, ResponsePolicyV1.update(response))

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    #   After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        return await datasets.update_response(db, search_engine, response, response_update)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.delete("/responses/{response_id}", response_model=ResponseSchema)
async def delete_response(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine=Depends(get_search_engine),
    response_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    response = await _get_response(db, response_id)

    await authorize(current_user, ResponsePolicyV1.delete(response))

    await datasets.delete_response(db, search_engine, response)

    return response
