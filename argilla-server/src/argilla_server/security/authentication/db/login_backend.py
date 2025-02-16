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

from starlette.authentication import AuthenticationBackend
from argilla_server.jobs.queues import REDIS_CONNECTION

MAX_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutes


class LoginAuthenticationBackend(AuthenticationBackend):
    """
    Authentication backend which locks the user out after a certain amount
    of wrong attempts to login
    """

    def __init__(self):
        self.redis = REDIS_CONNECTION

    async def check_lockout(self, credential_key: str) -> bool:
        """Check if credential key (username or API key) is locked out"""
        key = f"failed_auth:{credential_key}"
        attempts = await self.redis.get(key)
        attempts = int(attempts or 0)
        if attempts >= MAX_ATTEMPTS:
            return False
        return True

    async def increase_lockout(self, credential_key: str) -> None:
        """Increment failed attempts"""
        key = f"failed_auth:{credential_key}"
        await self.redis.incr(key)

        # Ensure expiration is set after first failure
        ttl = await self.redis.ttl(key)
        if ttl == -1:  # Key exists but no expiration set
            await self.redis.expire(key, LOCKOUT_TIME)

    async def clear_lockout(self, credential_key: str) -> None:
        """Reset failed attempts on successful authentication"""
        key = f"failed_auth:{credential_key}"
        await self.redis.delete(key)
