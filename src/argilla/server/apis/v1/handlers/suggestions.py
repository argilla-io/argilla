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
from argilla.server.models import Suggestion, User
from argilla.server.policies import SuggestionPolicyV1, authorize
from argilla.server.schemas.v1.suggestions import Suggestion as SuggestionSchema
from argilla.server.security import auth

router = APIRouter(tags=["suggestions"])


async def _get_suggestion(db: "AsyncSession", suggestion_id: UUID) -> Suggestion:
    suggestion = await datasets.get_suggestion_by_id(db, suggestion_id)
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suggestion with id `{suggestion_id}` not found",
        )
    return suggestion


@router.delete("/suggestions/{suggestion_id}", response_model=SuggestionSchema)
async def delete_suggestion(
    *,
    db: AsyncSession = Depends(get_async_db),
    suggestion_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    suggestion = await _get_suggestion(db, suggestion_id)

    await authorize(current_user, SuggestionPolicyV1.delete(suggestion))

    try:
        return await datasets.delete_suggestion(db, suggestion)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
