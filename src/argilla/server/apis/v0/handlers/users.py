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

from fastapi import APIRouter, Depends, Request, Security
from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from argilla.server.commons import telemetry
from argilla.server.contexts import accounts
from argilla.server.database import get_db
from argilla.server.security import auth
from argilla.server.security.model import User, UserCreate

router = APIRouter(tags=["users"])


@router.get("/me", response_model=User, response_model_exclude_none=True, operation_id="whoami")
async def whoami(request: Request, current_user: User = Security(auth.get_user, scopes=[])):
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
    return current_user


@router.get("/users", response_model=List[User], response_model_exclude_none=True)
def list_users(*, db: Session = Depends(get_db), current_user: User = Security(auth.get_user, scopes=[])):
    users = accounts.list_users(db)

    return parse_obj_as(List[User], users)


@router.post("/users", response_model=User, response_model_exclude_none=True)
def create_user(
    *, db: Session = Depends(get_db), user_create: UserCreate, current_user: User = Security(auth.get_user, scopes=[])
):
    user = accounts.create_user(db, user_create)

    return User.from_orm(user)
