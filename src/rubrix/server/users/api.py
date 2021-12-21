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

from fastapi import APIRouter, Security
from rubrix.server.security import auth
from rubrix.server.security.model import User

router = APIRouter(tags=["users"])


@router.get(
    "/me",
    response_model=User,
    response_model_exclude_none=True,
    operation_id="whoami",
)
async def whoami(current_user: User = Security(auth.get_user, scopes=[])):
    """
    User info endpoint

    Parameters
    ----------
    current_user:
        The current request user

    Returns
    -------
        The current user

    """
    return current_user
