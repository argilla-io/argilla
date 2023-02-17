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

from argilla.server.database import SessionLocal
from argilla.server.models import User
from passlib.context import CryptContext
from sqlalchemy import select

_CRYPT_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_api_key(api_key: str):
    session = SessionLocal()

    return session.scalar(select(User).where(User.api_key == api_key))


def get_user_by_username(username):
    session = SessionLocal()

    return session.scalar(select(User).where(User.username == username))


def create_user(password, **params):
    session = SessionLocal()

    user = User(password_hash=_CRYPT_CONTEXT.hash(password), **params)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def authenticate_user(username, password):
    user = get_user_by_username(username)

    if user and _CRYPT_CONTEXT.verify(password, user.password_hash):
        return user
    elif user:
        return
    else:
        _CRYPT_CONTEXT.verify_dummy()
