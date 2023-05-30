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

import argilla.client.sdk.users.api as users_api
from argilla.client import active_client
from argilla.client.sdk.users.models import UserModel


class User:
    def __init__(self) -> None:
        pass

    @classmethod
    def create(cls) -> "User":
        return cls()


def list_users() -> List[UserModel]:
    return users_api.list_users(active_client().http_client.httpx).parsed
