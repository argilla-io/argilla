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
from sqlalchemy.orm import Session

from argilla.server.contexts import accounts
from argilla.server.database import get_db
from argilla.server.errors import EntityAlreadyExistsError, EntityNotFoundError
from argilla.server.policies import WorkspacePolicy, WorkspaceUserPolicy, authorize
from argilla.server.security import auth
from argilla.server.security.model import (
    User,
    Workspace,
    WorkspaceCreate,
    WorkspaceUserCreate,
)

router = APIRouter(tags=["workspaces"])


@router.get("/workspaces", response_model=List[Workspace], response_model_exclude_none=True)
def list_workspaces(*, db: Session = Depends(get_db), current_user: User = Security(auth.get_current_user)):
    authorize(current_user, WorkspacePolicy.list)

    workspaces = accounts.list_workspaces(db)

    return parse_obj_as(List[Workspace], workspaces)


@router.post("/workspaces", response_model=Workspace, response_model_exclude_none=True)
def create_workspace(
    *,
    db: Session = Depends(get_db),
    workspace_create: WorkspaceCreate,
    current_user: User = Security(auth.get_current_user),
):
    authorize(current_user, WorkspacePolicy.create)

    if accounts.get_workspace_by_name(db, workspace_create.name):
        raise EntityAlreadyExistsError(name=workspace_create.name, type=Workspace)

    workspace = accounts.create_workspace(db, workspace_create)

    return Workspace.from_orm(workspace)


# TODO: We can't do workspaces deletions right now. Workspaces are associated with datasets and used on
# ElasticSearch indexes. Once that we have datasets on the database and we can check if the workspace doesn't have
# any dataset then we can delete them.
# @router.delete("/workspaces/{workspace_id}", response_model=Workspace, response_model_exclude_none=True)
def delete_workspace(
    *, db: Session = Depends(get_db), workspace_id: UUID, current_user: User = Security(auth.get_current_user)
):
    workspace = accounts.get_workspace_by_id(db, workspace_id)
    if not workspace:
        raise EntityNotFoundError(name=str(workspace_id), type=Workspace)

    authorize(current_user, WorkspacePolicy.delete(workspace))

    accounts.delete_workspace(db, workspace)

    return Workspace.from_orm(workspace)


@router.get("/workspaces/{workspace_id}/users", response_model=List[User], response_model_exclude_none=True)
def list_workspace_users(
    *, db: Session = Depends(get_db), workspace_id: UUID, current_user: User = Security(auth.get_current_user)
):
    authorize(current_user, WorkspaceUserPolicy.list)

    workspace = accounts.get_workspace_by_id(db, workspace_id)
    if not workspace:
        raise EntityNotFoundError(name=str(workspace_id), type=Workspace)

    return parse_obj_as(List[User], workspace.users)


@router.post("/workspaces/{workspace_id}/users/{user_id}", response_model=User, response_model_exclude_none=True)
def create_workspace_user(
    *,
    db: Session = Depends(get_db),
    workspace_id: UUID,
    user_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    authorize(current_user, WorkspaceUserPolicy.create)

    workspace = accounts.get_workspace_by_id(db, workspace_id)
    if not workspace:
        raise EntityNotFoundError(name=str(workspace_id), type=Workspace)

    user = accounts.get_user_by_id(db, user_id)
    if not user:
        raise EntityNotFoundError(name=str(user_id), type=User)

    if accounts.get_workspace_user_by_workspace_id_and_user_id(db, workspace_id, user_id):
        raise EntityAlreadyExistsError(name=str(user_id), type=User)

    workspace_user = accounts.create_workspace_user(db, WorkspaceUserCreate(workspace_id=workspace_id, user_id=user_id))

    return User.from_orm(workspace_user.user)


@router.delete("/workspaces/{workspace_id}/users/{user_id}", response_model=User, response_model_exclude_none=True)
def delete_workspace_user(
    *,
    db: Session = Depends(get_db),
    workspace_id: UUID,
    user_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    workspace_user = accounts.get_workspace_user_by_workspace_id_and_user_id(db, workspace_id, user_id)
    if not workspace_user:
        raise EntityNotFoundError(name=str(user_id), type=User)

    authorize(current_user, WorkspaceUserPolicy.delete(workspace_user))

    user = workspace_user.user
    accounts.delete_workspace_user(db, workspace_user)

    return User.from_orm(user)
