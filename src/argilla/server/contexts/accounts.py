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

from argilla.server.models import User, Workspace, WorkspaceUser
from argilla.server.security.model import (
    UserCreate,
    WorkspaceCreate,
    WorkspaceUserCreate,
)
from passlib.context import CryptContext
from sqlalchemy.orm import Session

_CRYPT_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_workspace_user_by_workspace_id_and_user_id(db: Session, workspace_id: UUID, user_id: UUID):
    return db.query(WorkspaceUser).filter_by(workspace_id=workspace_id, user_id=user_id).first()


def create_workspace_user(db: Session, workspace_user_create: WorkspaceUserCreate):
    workspace_user = WorkspaceUser(
        workspace_id=workspace_user_create.workspace_id,
        user_id=workspace_user_create.user_id,
    )

    db.add(workspace_user)
    db.commit()
    db.refresh(workspace_user)

    return workspace_user


def delete_workspace_user(db: Session, workspace_user: WorkspaceUser):
    db.delete(workspace_user)
    db.commit()

    return workspace_user


def get_workspace_by_id(db: Session, workspace_id: UUID):
    return db.get(Workspace, workspace_id)


def get_workspace_by_name(db: Session, workspace_name: str):
    return db.query(Workspace).filter_by(name=workspace_name).first()


def list_workspaces(db: Session):
    return db.query(Workspace).order_by(Workspace.inserted_at.asc()).all()


def create_workspace(db: Session, workspace_create: WorkspaceCreate):
    workspace = Workspace(name=workspace_create.name)

    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    return workspace


def delete_workspace(db: Session, workspace: Workspace):
    db.delete(workspace)
    db.commit()

    return workspace


def get_user_by_id(db: Session, user_id: UUID):
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter_by(username=username).first()


def get_user_by_api_key(db: Session, api_key: str):
    return db.query(User).filter_by(api_key=api_key).first()


def list_users(db: Session):
    return db.query(User).order_by(User.inserted_at.asc()).all()


def create_user(db: Session, user_create: UserCreate):
    user = User(
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        username=user_create.username,
        role=user_create.role,
        password_hash=hash_password(user_create.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()

    return user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)

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
