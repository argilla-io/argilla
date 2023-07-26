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

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Security
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession

from argilla.server.contexts import accounts
from argilla.server.database import get_async_db
from argilla.server.errors import EntityAlreadyExistsError, EntityNotFoundError
from argilla.server.policies import WorkspacePolicy, WorkspaceUserPolicy, authorize
from argilla.server.security import auth
from argilla.server.security.model import User, Workspace, WorkspaceCreate, WorkspaceUserCreate

router = APIRouter(tags=["workspaces"])


@router.get("/workspaces", response_model=List[Workspace], response_model_exclude_none=True)
async def list_workspaces(
    *, db: AsyncSession = Depends(get_async_db), current_user: User = Security(auth.get_current_user)
):
    await authorize(current_user, WorkspacePolicy.list)

    workspaces = await accounts.list_workspaces(db)

    return parse_obj_as(List[Workspace], workspaces)


@router.post("/workspaces", response_model=Workspace, response_model_exclude_none=True)
async def create_workspace(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_create: WorkspaceCreate,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspacePolicy.create)

    if await accounts.get_workspace_by_name(db, workspace_create.name):
        raise EntityAlreadyExistsError(name=workspace_create.name, type=Workspace)

    workspace = await accounts.create_workspace(db, workspace_create)

    return Workspace.from_orm(workspace)


@router.get("/workspaces/{workspace_id}/users", response_model=List[User], response_model_exclude_none=True)
async def list_workspace_users(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspaceUserPolicy.list(workspace_id))

    workspace = await accounts.get_workspace_by_id(db, workspace_id)
    if not workspace:
        raise EntityNotFoundError(name=str(workspace_id), type=Workspace)

    await workspace.awaitable_attrs.users
    for user in workspace.users:
        await user.awaitable_attrs.workspaces
    return parse_obj_as(List[User], workspace.users)


@router.post("/workspaces/{workspace_id}/users/{user_id}", response_model=User, response_model_exclude_none=True)
async def create_workspace_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: UUID,
    user_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspaceUserPolicy.create)

    workspace = await accounts.get_workspace_by_id(db, workspace_id)
    if not workspace:
        raise EntityNotFoundError(name=str(workspace_id), type=Workspace)

    user = await accounts.get_user_by_id(db, user_id)
    if not user:
        raise EntityNotFoundError(name=str(user_id), type=User)

    workspace_user = await accounts.get_workspace_user_by_workspace_id_and_user_id(db, workspace_id, user_id)
    if workspace_user is not None:
        raise EntityAlreadyExistsError(name=str(user_id), type=User)

    workspace_user = await accounts.create_workspace_user(
        db, WorkspaceUserCreate(workspace_id=workspace_id, user_id=user_id)
    )
    await db.refresh(user, attribute_names=["workspaces"])

    return User.from_orm(workspace_user.user)


@router.delete("/workspaces/{workspace_id}/users/{user_id}", response_model=User, response_model_exclude_none=True)
async def delete_workspace_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: UUID,
    user_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    workspace_user = await accounts.get_workspace_user_by_workspace_id_and_user_id(db, workspace_id, user_id)
    if not workspace_user:
        raise EntityNotFoundError(name=str(user_id), type=User)

    await authorize(current_user, WorkspaceUserPolicy.delete(workspace_user))

    user = await workspace_user.awaitable_attrs.user
    await accounts.delete_workspace_user(db, workspace_user)
    await db.refresh(user, attribute_names=["workspaces"])

    return User.from_orm(user)
