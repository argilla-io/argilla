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

from typing import TYPE_CHECKING, List, Union
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from argilla.server.models import User, Workspace, WorkspaceUser
from argilla.server.security.model import (
    UserCreate,
    WorkspaceCreate,
    WorkspaceUserCreate,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

_CRYPT_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_workspace_user_by_workspace_id_and_user_id(
    db: "AsyncSession", workspace_id: UUID, user_id: UUID
) -> Union[WorkspaceUser, None]:
    result = await db.execute(select(WorkspaceUser).filter_by(workspace_id=workspace_id, user_id=user_id))
    return result.scalar_one_or_none()


async def create_workspace_user(db: "AsyncSession", workspace_user_create: WorkspaceUserCreate) -> WorkspaceUser:
    workspace_user = WorkspaceUser(
        workspace_id=workspace_user_create.workspace_id,
        user_id=workspace_user_create.user_id,
    )

    db.add(workspace_user)
    await db.commit()
    # db.refresh(workspace_user)

    return workspace_user


async def delete_workspace_user(db: "AsyncSession", workspace_user: WorkspaceUser) -> WorkspaceUser:
    await db.delete(workspace_user)
    await db.commit()
    return workspace_user


async def get_workspace_by_id(db: "AsyncSession", workspace_id: UUID) -> Workspace:
    return await db.get(Workspace, workspace_id)


async def get_workspace_by_name(db: "AsyncSession", workspace_name: str) -> Union[Workspace, None]:
    result = await db.execute(select(Workspace).filter_by(name=workspace_name))
    return result.scalar_one_or_none()


async def list_workspaces(db: "AsyncSession") -> List[Workspace]:
    result = await db.execute(select(Workspace).order_by(Workspace.inserted_at.asc()))
    return result.scalars().all()


async def create_workspace(db: "AsyncSession", workspace_create: WorkspaceCreate) -> Workspace:
    workspace = Workspace(name=workspace_create.name)

    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)

    return workspace


async def delete_workspace(db: "AsyncSession", workspace: Workspace):
    await db.delete(workspace)
    await db.commit()
    return workspace


async def get_user_by_id(db: Session, user_id: UUID) -> Union[User, None]:
    return await db.get(User, user_id)


def get_user_by_username_sync(db: Session, username: str) -> Union[User, None]:
    return db.query(User).filter_by(username=username).first()


async def get_user_by_username(db: "AsyncSession", username: str) -> Union[User, None]:
    result = await db.execute(select(User).filter_by(username=username).options(selectinload(User.workspaces)))
    return result.scalar_one_or_none()


def get_user_by_api_key_sync(db: Session, api_key: str) -> Union[User, None]:
    return db.query(User).filter_by(api_key=api_key).first()


async def get_user_by_api_key(db: "AsyncSession", api_key: str) -> Union[User, None]:
    result = await db.execute(select(User).where(User.api_key == api_key).options(selectinload(User.workspaces)))
    return result.scalar_one_or_none()


def list_users(db: Session):
    return db.query(User).order_by(User.inserted_at.asc()).all()


async def create_user(db: "AsyncSession", user_create: UserCreate) -> User:
    user = User(
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        username=user_create.username,
        role=user_create.role,
        password_hash=hash_password(user_create.password),
    )

    db.add(user)
    await db.commit()
    await user.awaitable_attrs.workspaces

    return user


async def delete_user(db: "AsyncSession", user: User) -> User:
    await db.delete(user)
    await db.commit()
    return user


async def authenticate_user(db: Session, username: str, password: str):
    user = await get_user_by_username(db, username)

    if user and verify_password(password, user.password_hash):
        return user
    elif user:
        return
    else:
        _CRYPT_CONTEXT.dummy_verify()


def hash_password(password: str):
    return _CRYPT_CONTEXT.hash(password)


def verify_password(password: str, password_hash: str):
    return _CRYPT_CONTEXT.verify(password, password_hash)
