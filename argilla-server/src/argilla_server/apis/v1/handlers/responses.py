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

from argilla_server.contexts import datasets
from argilla_server.database import get_async_db
from argilla_server.errors.future import NotFoundError
from argilla_server.models import Response, User
from argilla_server.policies import ResponsePolicyV1, authorize
from argilla_server.schemas.v1.responses import Response as ResponseSchema
from argilla_server.schemas.v1.responses import (
    ResponsesBulk,
    ResponsesBulkCreate,
    ResponseUpdate,
)
from argilla_server.search_engine import SearchEngine, get_search_engine
from argilla_server.security import auth
from argilla_server.use_cases.responses.upsert_responses_in_bulk import (
    UpsertResponsesInBulkUseCase,
    UpsertResponsesInBulkUseCaseFactory,
)

router = APIRouter(tags=["responses"])


async def _get_response(db: AsyncSession, response_id: UUID) -> Response:
    response = await datasets.get_response_by_id(db, response_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Response with id `{response_id}` not found",
        )

    return response


@router.post("/me/responses/bulk", response_model=ResponsesBulk)
async def create_current_user_responses_bulk(
    *,
    body: ResponsesBulkCreate,
    current_user: User = Security(auth.get_current_user),
    use_case: UpsertResponsesInBulkUseCase = Depends(UpsertResponsesInBulkUseCaseFactory()),
):
    try:
        responses_bulk_items = await use_case.execute(body.items, user=current_user)
    except NotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    else:
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
