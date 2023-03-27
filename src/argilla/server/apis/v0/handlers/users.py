#  coding=utf-8
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

from fastapi import APIRouter, Depends, Request, Security
from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from argilla.server import models
from argilla.server.commons import telemetry
from argilla.server.contexts import accounts
from argilla.server.database import get_db
from argilla.server.errors import EntityAlreadyExistsError, EntityNotFoundError
from argilla.server.policies import UserPolicy, authorize
from argilla.server.security import auth
from argilla.server.security.model import User, UserCreate

router = APIRouter(tags=["users"])


@router.get("/me", response_model=User, response_model_exclude_none=True, operation_id="whoami")
async def whoami(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Security(auth.get_current_user),
):
    """
    User info endpoint

    Parameters
    ----------
    request:
        The original request
    current_user:
        The current request user

    Returns
    -------
        The current user

    """

    await telemetry.track_login(request, username=current_user.username)

    user = User.from_orm(current_user)
    # TODO: The current client checks if a user can work on a specific workspace
    #  by using workspaces info returning in `/api/me`.
    #  Returning all workspaces from the `/api/me` for admin users keeps the
    #  backward compatibility with the client flow.
    #  This logic will be removed in future versions, when python client
    #  start using the list workspaces (`/api/workspaces`) endpoint to handle
    #  accessible workspaces for connected user.
    if current_user.is_admin:
        workspaces = accounts.list_workspaces(db)
        user.workspaces = [workspace.name for workspace in workspaces]

    return user


@router.get("/users", response_model=List[User], response_model_exclude_none=True)
def list_users(*, db: Session = Depends(get_db), current_user: models.User = Security(auth.get_current_user)):
    authorize(current_user, UserPolicy.list)

    users = accounts.list_users(db)

    return parse_obj_as(List[User], users)


@router.post("/users", response_model=User, response_model_exclude_none=True)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_create: UserCreate,
    current_user: models.User = Security(auth.get_current_user),
):
    authorize(current_user, UserPolicy.create)

    if accounts.get_user_by_username(db, user_create.username):
        raise EntityAlreadyExistsError(name=user_create.username, type=User)

    user = accounts.create_user(db, user_create)

    return User.from_orm(user)


@router.delete("/users/{user_id}", response_model=User, response_model_exclude_none=True)
def delete_user(
    *, db: Session = Depends(get_db), user_id: UUID, current_user: models.User = Security(auth.get_current_user)
):
    user = accounts.get_user_by_id(db, user_id)
    if not user:
        # TODO: Forcing here user_id to be an string.
        # Not casting it is causing a `Object of type UUID is not JSON serializable`.
        # Possible solution redefining JSONEncoder.default here:
        # https://github.com/jazzband/django-push-notifications/issues/586
        raise EntityNotFoundError(name=str(user_id), type=User)

    authorize(current_user, UserPolicy.delete(user))

    accounts.delete_user(db, user)

    return User.from_orm(user)
