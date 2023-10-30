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
from sqlalchemy import exists, select
from sqlalchemy.orm import Session, selectinload

from argilla.server.models import User, Workspace, WorkspaceUser
from argilla.server.security.model import UserCreate, WorkspaceCreate, WorkspaceUserCreate

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

_CRYPT_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_workspace_user_by_workspace_id_and_user_id(
    db: "AsyncSession", workspace_id: UUID, user_id: UUID
) -> Union[WorkspaceUser, None]:
    result = await db.execute(select(WorkspaceUser).filter_by(workspace_id=workspace_id, user_id=user_id))
    return result.scalar_one_or_none()


async def create_workspace_user(db: "AsyncSession", workspace_user_create: WorkspaceUserCreate) -> WorkspaceUser:
    workspace_user = await WorkspaceUser.create(
        db,
        workspace_id=workspace_user_create.workspace_id,
        user_id=workspace_user_create.user_id,
    )
    await db.refresh(workspace_user, attribute_names=["workspace", "user"])
    return workspace_user


async def delete_workspace_user(db: "AsyncSession", workspace_user: WorkspaceUser) -> WorkspaceUser:
    return await workspace_user.delete(db)


async def get_workspace_by_id(db: "AsyncSession", workspace_id: UUID) -> Workspace:
    return await Workspace.read(db, id=workspace_id)


async def get_workspace_by_name(db: "AsyncSession", workspace_name: str) -> Union[Workspace, None]:
    result = await db.execute(select(Workspace).filter_by(name=workspace_name))
    return result.scalar_one_or_none()


async def list_workspaces(db: "AsyncSession") -> List[Workspace]:
    result = await db.execute(select(Workspace).order_by(Workspace.inserted_at.asc()))
    return result.scalars().all()


async def list_workspaces_by_user_id(db: "AsyncSession", user_id: UUID) -> List[Workspace]:
    result = await db.execute(
        select(Workspace)
        .join(WorkspaceUser)
        .filter(WorkspaceUser.user_id == user_id)
        .order_by(Workspace.inserted_at.asc())
    )
    return result.scalars().all()


async def create_workspace(db: "AsyncSession", workspace_create: WorkspaceCreate) -> Workspace:
    return await Workspace.create(db, schema=workspace_create)


async def delete_workspace(db: "AsyncSession", workspace: Workspace):
    return await workspace.delete(db)


async def get_user_by_id(db: "AsyncSession", user_id: UUID) -> Union[User, None]:
    return await User.read(db, id=user_id)


async def user_exists(db: "AsyncSession", user_id: UUID) -> bool:
    return await db.scalar(select(exists().where(User.id == user_id)))


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


async def list_users(db: "AsyncSession") -> List[User]:
    result = await db.execute(select(User).order_by(User.inserted_at.asc()).options(selectinload(User.workspaces)))
    return result.scalars().all()


async def create_user(db: "AsyncSession", user_create: UserCreate) -> User:
    async with db.begin_nested():
        user = await User.create(
            db,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            username=user_create.username,
            role=user_create.role,
            password_hash=hash_password(user_create.password),
            autocommit=False,
        )

        if user_create.workspaces:
            for workspace_name in user_create.workspaces:
                workspace = await get_workspace_by_name(db, workspace_name)
                if not workspace:
                    raise ValueError(f"Workspace '{workspace_name}' does not exist")
                await WorkspaceUser.create(
                    db,
                    workspace_id=workspace.id,
                    user_id=user.id,
                    autocommit=False,
                )

    await db.commit()

    return user


async def delete_user(db: "AsyncSession", user: User) -> User:
    return await user.delete(db)


async def authenticate_user(db: Session, username: str, password: str):
    user = await get_user_by_username(db, username)

    if user and verify_password(password, user.password_hash):
        return user
    elif user:
        return
    else:
        _CRYPT_CONTEXT.dummy_verify()


def hash_password(password: str) -> str:
    return _CRYPT_CONTEXT.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _CRYPT_CONTEXT.verify(password, password_hash)
