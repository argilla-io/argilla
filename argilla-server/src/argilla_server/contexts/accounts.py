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
import secrets
from typing import Iterable, List, Sequence, Union
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from argilla_server.contexts import datasets
from argilla_server.enums import UserRole
from argilla_server.errors.future import NotUniqueError, UnprocessableEntityError
from argilla_server.models import User, Workspace, WorkspaceUser
from argilla_server.security.authentication.jwt import JWT
from argilla_server.security.authentication.userinfo import UserInfo

_CRYPT_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_workspace_user(db: AsyncSession, workspace_user_attrs: dict) -> WorkspaceUser:
    workspace_id = workspace_user_attrs["workspace_id"]
    user_id = workspace_user_attrs["user_id"]

    if await WorkspaceUser.get_by(db, workspace_id=workspace_id, user_id=user_id) is not None:
        raise NotUniqueError(f"Workspace user with workspace_id `{workspace_id}` and user_id `{user_id}` is not unique")

    workspace_user = await WorkspaceUser.create(db, workspace_id=workspace_id, user_id=user_id)

    # TODO: Once we delete API v0 endpoint we can reduce this to refresh only the user.
    await db.refresh(workspace_user, attribute_names=["workspace", "user"])

    return workspace_user


async def delete_workspace_user(db: AsyncSession, workspace_user: WorkspaceUser) -> WorkspaceUser:
    return await workspace_user.delete(db)


async def list_workspaces(db: AsyncSession) -> List[Workspace]:
    result = await db.execute(select(Workspace).order_by(Workspace.inserted_at.asc()))
    return result.scalars().all()


async def list_workspaces_by_user_id(db: AsyncSession, user_id: UUID) -> List[Workspace]:
    result = await db.execute(
        select(Workspace)
        .join(WorkspaceUser)
        .filter(WorkspaceUser.user_id == user_id)
        .order_by(Workspace.inserted_at.asc())
    )
    return result.scalars().all()


async def create_workspace(db: AsyncSession, workspace_attrs: dict) -> Workspace:
    if await Workspace.get_by(db, name=workspace_attrs["name"]) is not None:
        raise NotUniqueError(f"Workspace name `{workspace_attrs['name']}` is not unique")

    return await Workspace.create(db, name=workspace_attrs["name"])


async def delete_workspace(db: AsyncSession, workspace: Workspace):
    if await datasets.list_datasets(db, workspace_id=workspace.id):
        raise NotUniqueError(f"Cannot delete the workspace {workspace.id}. This workspace has some datasets linked")

    return await workspace.delete(db)


async def user_exists(db: AsyncSession, user_id: UUID) -> bool:
    return await db.scalar(select(exists().where(User.id == user_id)))


async def get_user_by_username(db: AsyncSession, username: str) -> Union[User, None]:
    result = await db.execute(select(User).filter_by(username=username).options(selectinload(User.workspaces)))
    return result.scalar_one_or_none()


async def get_user_by_api_key(db: AsyncSession, api_key: str) -> Union[User, None]:
    result = await db.execute(select(User).where(User.api_key == api_key).options(selectinload(User.workspaces)))
    return result.scalar_one_or_none()


async def list_users(db: "AsyncSession") -> Sequence[User]:
    # TODO: After removing API v0 implementation we can remove the workspaces eager loading
    # because is not used in the new API v1 endpoints.
    result = await db.execute(select(User).order_by(User.inserted_at.asc()).options(selectinload(User.workspaces)))
    return result.scalars().all()


async def list_users_by_ids(db: AsyncSession, ids: Iterable[UUID]) -> Sequence[User]:
    result = await db.execute(select(User).filter(User.id.in_(ids)))
    return result.scalars().all()


# TODO: After removing API v0 implementation we can remove the workspaces attribute.
# With API v1 the workspaces will be created doing additional requests to other endpoints for it.
async def create_user(db: AsyncSession, user_attrs: dict, workspaces: Union[List[str], None] = None) -> User:
    if await get_user_by_username(db, user_attrs["username"]) is not None:
        raise NotUniqueError(f"User username `{user_attrs['username']}` is not unique")

    user = await User.create(
        db,
        first_name=user_attrs["first_name"],
        last_name=user_attrs["last_name"],
        username=user_attrs["username"],
        role=user_attrs["role"],
        password_hash=hash_password(user_attrs["password"]),
        autocommit=False,
    )

    if workspaces is not None:
        for workspace_name in workspaces:
            workspace = await Workspace.get_by(db, name=workspace_name)
            if not workspace:
                raise UnprocessableEntityError(f"Workspace '{workspace_name}' does not exist")

            await WorkspaceUser.create(
                db,
                workspace_id=workspace.id,
                user_id=user.id,
                autocommit=False,
            )

    await db.commit()

    return user


async def create_user_with_random_password(
    db,
    username: str,
    first_name: str,
    role: UserRole = UserRole.annotator,
    workspaces: Union[List[str], None] = None,
) -> User:
    user_attrs = {
        "first_name": first_name,
        "last_name": None,
        "username": username,
        "role": role,
        "password": _generate_random_password(),
    }

    return await create_user(db, user_attrs, workspaces)


async def delete_user(db: AsyncSession, user: User) -> User:
    return await user.delete(db)


async def authenticate_user(db: AsyncSession, username: str, password: str):
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


def _generate_random_password() -> str:
    return secrets.token_urlsafe()


def generate_user_token(user: User) -> str:
    return JWT.create(
        UserInfo(
            identity=str(user.id),
            name=user.first_name,
            username=user.username,
            role=user.role,
        ),
    )
