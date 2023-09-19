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

from argilla.server.contexts import accounts
from argilla.server.database import get_async_db
from argilla.server.models import User
from argilla.server.policies import UserPolicyV1, authorize
from argilla.server.schemas.v1.workspaces import Workspaces
from argilla.server.security import auth

router = APIRouter(tags=["users"])


@router.get("/users/{user_id}/workspaces", response_model=Workspaces)
async def list_user_workspaces(
    *, db: AsyncSession = Depends(get_async_db), user_id: UUID, current_user: User = Security(auth.get_current_user)
):
    await authorize(current_user, UserPolicyV1.list_workspaces)

    user = await accounts.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id `{user_id}` not found",
        )

    if user.is_owner:
        workspaces = await accounts.list_workspaces(db)
    else:
        workspaces = await accounts.list_workspaces_by_user_id(db, user_id)

    return Workspaces(items=workspaces)
