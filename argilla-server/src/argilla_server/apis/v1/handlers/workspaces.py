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

from argilla_server import models
from argilla_server.contexts import accounts, datasets
from argilla_server.database import get_async_db
from argilla_server.errors import EntityAlreadyExistsError
from argilla_server.errors.future import NotUniqueError
from argilla_server.models import User
from argilla_server.policies import WorkspacePolicyV1, WorkspaceUserPolicyV1, authorize
from argilla_server.schemas.v1.users import User, Users
from argilla_server.schemas.v1.workspaces import Workspace, WorkspaceCreate, Workspaces, WorkspaceUserCreate
from argilla_server.security import auth
from argilla_server.services.datasets import DatasetsService

router = APIRouter(tags=["workspaces"])


@router.get("/workspaces/{workspace_id}", response_model=Workspace)
async def get_workspace(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: UUID,
    current_user: models.User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspacePolicyV1.get(workspace_id))

    workspace = await accounts.get_workspace_by_id(db, workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with id `{workspace_id}` not found",
        )

    return workspace


@router.post("/workspaces", status_code=status.HTTP_201_CREATED, response_model=Workspace)
async def create_workspace(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_create: WorkspaceCreate,
    current_user: models.User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspacePolicyV1.create)

    try:
        workspace = await accounts.create_workspace(db, workspace_create.dict())
    except NotUniqueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return workspace


@router.delete("/workspaces/{workspace_id}", response_model=Workspace)
async def delete_workspace(
    *,
    db: AsyncSession = Depends(get_async_db),
    datasets_service: DatasetsService = Depends(DatasetsService.get_instance),
    workspace_id: UUID,
    current_user: models.User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspacePolicyV1.delete)

    workspace = await accounts.get_workspace_by_id(db, workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with id `{workspace_id}` not found",
        )

    if await datasets.list_datasets_by_workspace_id(db, workspace_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete the workspace {workspace_id}. This workspace has some feedback datasets linked",
        )

    if await datasets_service.list(current_user, workspaces=[workspace.name]):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete the workspace {workspace_id}. This workspace has some datasets linked",
        )

    return await accounts.delete_workspace(db, workspace)


@router.get("/me/workspaces", response_model=Workspaces)
async def list_workspaces_me(
    *,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Security(auth.get_current_user),
) -> Workspaces:
    await authorize(current_user, WorkspacePolicyV1.list_workspaces_me)

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
    current_user: models.User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspaceUserPolicyV1.list(workspace_id))

    workspace = await accounts.get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with id `{workspace_id}` not found",
        )

    await workspace.awaitable_attrs.users

    return Users(items=workspace.users)


@router.post("/workspaces/{workspace_id}/users", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_workspace_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: UUID,
    workspace_user_create: WorkspaceUserCreate,
    current_user: models.User = Security(auth.get_current_user),
):
    await authorize(current_user, WorkspaceUserPolicyV1.create)

    workspace = await accounts.get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with id `{workspace_id}` not found",
        )

    user = await accounts.get_user_by_id(db, workspace_user_create.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"User with id `{workspace_user_create.user_id}` not found",
        )

    try:
        workspace_user = await accounts.create_workspace_user(db, {"workspace_id": workspace.id, "user_id": user.id})
    except NotUniqueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return workspace_user.user


@router.delete("/workspaces/{workspace_id}/users/{user_id}", response_model=User)
async def delete_workspace_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: UUID,
    user_id: UUID,
    current_user: models.User = Security(auth.get_current_user),
):
    workspace_user = await accounts.get_workspace_user_by_workspace_id_and_user_id(db, workspace_id, user_id)
    if workspace_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id `{user_id}` not found in workspace with id `{workspace_id}`",
        )

    await authorize(current_user, WorkspaceUserPolicyV1.delete(workspace_user))

    await accounts.delete_workspace_user(db, workspace_user)

    return await workspace_user.awaitable_attrs.user
