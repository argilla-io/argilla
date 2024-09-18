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

from typing import Awaitable, Callable

from argilla_server.errors import ForbiddenOperationError
from argilla_server.models import User

PolicyAction = Callable[[User], Awaitable[bool]]


async def authorize(actor: User, policy_action: PolicyAction) -> None:
    if not await is_authorized(actor, policy_action):
        raise ForbiddenOperationError()


async def is_authorized(actor: User, policy_action: PolicyAction) -> bool:
    return await policy_action(actor)
