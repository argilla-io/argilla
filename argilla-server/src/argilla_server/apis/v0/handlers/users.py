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

from fastapi import APIRouter, Depends, HTTPException, Request, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server import models, telemetry
from argilla_server.contexts import accounts
from argilla_server.database import get_async_db
from argilla_server.errors import EntityAlreadyExistsError, EntityNotFoundError
from argilla_server.errors.future import NotUniqueError
from argilla_server.policies import UserPolicy, authorize
from argilla_server.pydantic_v1 import parse_obj_as
from argilla_server.schemas.v0.users import User, UserCreate
from argilla_server.security import auth

router = APIRouter(tags=["users"])


@router.get("/me", response_model=User, response_model_exclude_none=True, operation_id="whoami")
async def whoami(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
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

    await telemetry.track_login(request, current_user)

    user = User.from_orm(current_user)
    # TODO: The current client checks if a user can work on a specific workspace
    #  by using workspaces info returning in `/api/me`.
    #  Returning all workspaces from the `/api/me` for owner users keeps the
    #  backward compatibility with the client flow.
    #  This logic will be removed in future versions, when python client
    #  start using the list workspaces (`/api/v1/me/workspaces`) endpoint to handle
    #  accessible workspaces for connected user.
    if current_user.is_owner:
        workspaces = await accounts.list_workspaces(db)
        user.workspaces = [workspace.name for workspace in workspaces]

    return user


@router.get("/users", response_model=List[User], response_model_exclude_none=True)
async def list_users(
    *, db: AsyncSession = Depends(get_async_db), current_user: models.User = Security(auth.get_current_user)
):
    await authorize(current_user, UserPolicy.list)

    users = await accounts.list_users(db)

    return parse_obj_as(List[User], users)


@router.post("/users", response_model=User, response_model_exclude_none=True)
async def create_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    user_create: UserCreate,
    current_user: models.User = Security(auth.get_current_user),
):
    await authorize(current_user, UserPolicy.create)

    try:
        user = await accounts.create_user(db, user_create.dict(), user_create.workspaces)

        telemetry.track_user_created(user)
    except NotUniqueError:
        raise EntityAlreadyExistsError(name=user_create.username, type=User)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    await user.awaitable_attrs.workspaces

    return User.from_orm(user)


@router.delete("/users/{user_id}", response_model=User, response_model_exclude_none=True)
async def delete_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    user_id: UUID,
    current_user: models.User = Security(auth.get_current_user),
):
    user = await accounts.get_user_by_id(db, user_id)
    if not user:
        # TODO: Forcing here user_id to be an string.
        # Not casting it is causing a `Object of type UUID is not JSON serializable`.
        # Possible solution redefining JSONEncoder.default here:
        # https://github.com/jazzband/django-push-notifications/issues/586
        raise EntityNotFoundError(name=str(user_id), type=User)

    await authorize(current_user, UserPolicy.delete(user))

    await accounts.delete_user(db, user)

    return User.from_orm(user)
