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

from fastapi import APIRouter, Depends, Request, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.api.policies.v1 import UserPolicy, authorize
from argilla_server.api.schemas.v1.users import User as UserSchema
from argilla_server.api.schemas.v1.users import UserCreate, Users, UserUpdate
from argilla_server.api.schemas.v1.workspaces import Workspaces
from argilla_server.contexts import accounts
from argilla_server.database import get_async_db
from argilla_server.models import User
from argilla_server.security import auth

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserSchema)
async def get_current_user(
    current_user: User = Security(auth.get_current_user),
):
    return current_user


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    user_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, UserPolicy.get)

    return await User.get_or_raise(db, user_id)


@router.get("/users", response_model=Users)
async def list_users(
    *,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, UserPolicy.list)

    users = await accounts.list_users(db)

    return Users(items=users)


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def create_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    user_create: UserCreate,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, UserPolicy.create)

    user = await accounts.create_user(db, user_create.dict())

    return user


@router.delete("/users/{user_id}", response_model=UserSchema)
async def delete_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    user_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    user = await User.get_or_raise(db, user_id)

    await authorize(current_user, UserPolicy.delete)

    return await accounts.delete_user(db, user)

@router.patch("/users/{user_id}",status_code=status.HTTP_200_OK, response_model=UserSchema)
async def update_user(
    *,
    db: AsyncSession = Depends(get_async_db),
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Security(auth.get_current_user),):
        user = await User.get_or_raise(db, user_id)

        await authorize(current_user, UserPolicy.update)

        return await accounts.update_user(db, user, user_update.dict())

@router.get("/users/{user_id}/workspaces", response_model=Workspaces)
async def list_user_workspaces(
    *,
    db: AsyncSession = Depends(get_async_db),
    user_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, UserPolicy.list_workspaces)

    user = await User.get_or_raise(db, user_id)

    if user.is_owner:
        workspaces = await accounts.list_workspaces(db)
    else:
        workspaces = await accounts.list_workspaces_by_user_id(db, user_id)

    return Workspaces(items=workspaces)
