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
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.contexts import accounts
from argilla_server.database import get_async_db
from argilla_server.errors import EntityAlreadyExistsError, EntityNotFoundError
from argilla_server.errors.future import NotUniqueError
from argilla_server.policies import WorkspacePolicy, WorkspaceUserPolicy, authorize
from argilla_server.pydantic_v1 import parse_obj_as
from argilla_server.schemas.v0.users import User
from argilla_server.schemas.v0.workspaces import Workspace, WorkspaceCreate
from argilla_server.security import auth

router = APIRouter(tags=["workspaces"])


@router.post("/workspaces", response_model=Workspace, response_model_exclude_none=True)
async def create_workspace(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_create: WorkspaceCreate,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspacePolicy.create)

    try:
        workspace = await accounts.create_workspace(db, workspace_create.dict())
    except NotUniqueError:
        raise EntityAlreadyExistsError(name=workspace_create.name, type=Workspace)

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

    try:
        workspace_user = await accounts.create_workspace_user(db, {"workspace_id": workspace_id, "user_id": user_id})
    except NotUniqueError:
        raise EntityAlreadyExistsError(name=str(user_id), type=User)

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
