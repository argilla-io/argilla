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

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.api.policies.v1 import WorkspacePolicy, WorkspaceUserPolicy, authorize
from argilla_server.api.schemas.v1.users import User as UserSchema
from argilla_server.api.schemas.v1.users import Users
from argilla_server.api.schemas.v1.workspaces import (
    Workspace as WorkspaceSchema,
)
from argilla_server.api.schemas.v1.workspaces import (
    WorkspaceCreate,
    Workspaces,
    WorkspaceUserCreate,
)
from argilla_server.contexts import accounts
from argilla_server.database import get_async_db
from argilla_server.errors.future import NotFoundError, UnprocessableEntityError
from argilla_server.models import User, Workspace, WorkspaceUser
from argilla_server.security import auth

router = APIRouter(tags=["workspaces"])


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceSchema)
async def get_workspace(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspacePolicy.get(workspace_id))

    return await Workspace.get_or_raise(db, workspace_id)


@router.post("/workspaces", status_code=status.HTTP_201_CREATED, response_model=WorkspaceSchema)
async def create_workspace(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_create: WorkspaceCreate,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspacePolicy.create)

    return await accounts.create_workspace(db, workspace_create.dict())


@router.delete("/workspaces/{workspace_id}", response_model=WorkspaceSchema)
async def delete_workspace(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspacePolicy.delete)

    workspace = await Workspace.get_or_raise(db, workspace_id)

    return await accounts.delete_workspace(db, workspace)


@router.get("/me/workspaces", response_model=Workspaces)
async def list_workspaces_me(
    *,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Security(auth.get_current_user),
) -> Workspaces:
    await authorize(current_user, WorkspacePolicy.list_workspaces_me)

    if current_user.is_owner:
        workspaces = await accounts.list_workspaces(db)
    else:
        workspaces = await accounts.list_workspaces_by_user_id(db, current_user.id)

    return Workspaces(items=workspaces)


@router.get("/workspaces/{workspace_id}/users", response_model=Users)
async def list_workspace_users(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspaceUserPolicy.list(workspace_id))

    workspace = await Workspace.get_or_raise(db, workspace_id)

    await workspace.awaitable_attrs.users

    return Users(items=workspace.users)


@router.post("/workspaces/{workspace_id}/users", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def create_workspace_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: UUID,
    workspace_user_create: WorkspaceUserCreate,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspaceUserPolicy.create)

    workspace = await Workspace.get_or_raise(db, workspace_id)

    try:
        user = await User.get_or_raise(db, workspace_user_create.user_id)
    except NotFoundError as e:
        raise UnprocessableEntityError(e.message)

    workspace_user = await accounts.create_workspace_user(db, {"workspace_id": workspace.id, "user_id": user.id})

    return workspace_user.user


@router.delete("/workspaces/{workspace_id}/users/{user_id}", response_model=UserSchema)
async def delete_workspace_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: UUID,
    user_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    workspace_user = await WorkspaceUser.get_by_or_raise(db, workspace_id=workspace_id, user_id=user_id)

    await authorize(current_user, WorkspaceUserPolicy.delete(workspace_user))

    await accounts.delete_workspace_user(db, workspace_user)

    return await workspace_user.awaitable_attrs.user
