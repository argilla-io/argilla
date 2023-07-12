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
from argilla.server.policies import WorkspacePolicyV1, authorize
from argilla.server.schemas.v1.workspaces import Workspace, Workspaces
from argilla.server.security import auth
from argilla.server.security.model import User

router = APIRouter(tags=["workspaces"])


@router.get("/workspaces/{workspace_id}", response_model=Workspace)
async def get_workspace(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspacePolicyV1.get(workspace_id))

    workspace = await accounts.get_workspace_by_id(db, workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with id `{workspace_id}` not found",
        )

    return workspace


@router.get("/me/workspaces", response_model=Workspaces)
async def list_workspaces_me(
    *,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Security(auth.get_current_user),
) -> Workspaces:
    await authorize(current_user, WorkspacePolicyV1.list_workspaces_me)

    workspaces = await accounts.list_workspaces_by_user_id(db, current_user.id)
    return Workspaces(items=workspaces)
