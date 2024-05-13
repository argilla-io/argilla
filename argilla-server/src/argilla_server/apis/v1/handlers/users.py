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
from argilla_server.errors.future import NotUniqueError
from argilla_server.policies import UserPolicyV1, authorize
from argilla_server.schemas.v1.users import User, UserCreate, Users
from argilla_server.schemas.v1.workspaces import Workspaces
from argilla_server.security import auth

router = APIRouter(tags=["users"])


@router.get("/me", response_model=User)
async def get_current_user(request: Request, current_user: models.User = Security(auth.get_current_user)):
    await telemetry.track_login(request, current_user)

    return current_user


@router.get("/users/{user_id}", response_model=User)
async def get_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    user_id: UUID,
    current_user: models.User = Security(auth.get_current_user),
):
    await authorize(current_user, UserPolicyV1.get)

    user = await accounts.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id `{user_id}` not found",
        )

    return user


@router.get("/users", response_model=Users)
async def list_users(
    *,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Security(auth.get_current_user),
):
    await authorize(current_user, UserPolicyV1.list)

    users = await accounts.list_users(db)

    return Users(items=users)


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    user_create: UserCreate,
    current_user: models.User = Security(auth.get_current_user),
):
    await authorize(current_user, UserPolicyV1.create)

    try:
        user = await accounts.create_user(db, user_create.dict())

        telemetry.track_user_created(user)
    except NotUniqueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return user


@router.delete("/users/{user_id}", response_model=User)
async def delete_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    user_id: UUID,
    current_user: models.User = Security(auth.get_current_user),
):
    user = await accounts.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id `{user_id}` not found",
        )

    await authorize(current_user, UserPolicyV1.delete)

    await accounts.delete_user(db, user)

    return user


@router.get("/users/{user_id}/workspaces", response_model=Workspaces)
async def list_user_workspaces(
    *,
    db: AsyncSession = Depends(get_async_db),
    user_id: UUID,
    current_user: models.User = Security(auth.get_current_user),
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
