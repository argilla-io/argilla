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

from argilla_server.api.policies.v1.commons import PolicyAction
from argilla_server.models import User


class WorkspacePolicy:
    @classmethod
    def get(cls, workspace_id: UUID) -> PolicyAction:
        async def is_allowed(actor: User) -> bool:
            return actor.is_owner or await actor.is_member(workspace_id)

        return is_allowed

    @classmethod
    async def create(cls, actor: User) -> bool:
        return actor.is_owner

    @classmethod
    async def delete(cls, actor: User) -> bool:
        return actor.is_owner

    @classmethod
    async def list_workspaces_me(cls, actor: User) -> bool:
        return True
