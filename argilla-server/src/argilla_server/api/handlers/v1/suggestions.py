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

from argilla_server.api.policies.v1 import SuggestionPolicy, authorize
from argilla_server.api.schemas.v1.suggestions import Suggestion as SuggestionSchema
from argilla_server.contexts import datasets
from argilla_server.database import get_async_db
from argilla_server.models import Record, Suggestion, User
from argilla_server.search_engine import SearchEngine, get_search_engine
from argilla_server.security import auth

router = APIRouter(tags=["suggestions"])


@router.delete("/suggestions/{suggestion_id}", response_model=SuggestionSchema)
async def delete_suggestion(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    suggestion_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    suggestion = await Suggestion.get_or_raise(
        db,
        suggestion_id,
        options=[
            selectinload(Suggestion.record).selectinload(Record.dataset),
            selectinload(Suggestion.question),
        ],
    )

    await authorize(current_user, SuggestionPolicy.delete(suggestion))

    return await datasets.delete_suggestion(db, search_engine, suggestion)
