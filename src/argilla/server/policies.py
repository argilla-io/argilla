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

from argilla.server.errors import ForbiddenOperationError
from argilla.server.models import User, UserRole, Workspace, WorkspaceUser


class WorkspaceUserPolicy:
    @classmethod
    def list(cls, actor: User, workspace_user: WorkspaceUser) -> bool:
        return actor.role == UserRole.admin

    @classmethod
    def create(cls, actor: User, workspace_user: WorkspaceUser) -> bool:
        return actor.role == UserRole.admin

    @classmethod
    def delete(cls, actor: User, workspace_user: WorkspaceUser) -> bool:
        return actor.role == UserRole.admin


class WorkspacePolicy:
    @classmethod
    def list(cls, actor: User, workspace: Workspace) -> bool:
        return True

    @classmethod
    def create(cls, actor: User, workspace: Workspace) -> bool:
        # TODO: Once we receive ORM User models instead of Pydantic schema for current_user we can
        # change role checks to use `actor.is_admin` or `actor.is_annotator`
        return actor.role == UserRole.admin

    @classmethod
    def delete(cls, actor: User, workspace: Workspace) -> bool:
        return actor.role == UserRole.admin


class UserPolicy:
    @classmethod
    def list(cls, actor: User, user: User) -> bool:
        return actor.role == UserRole.admin

    @classmethod
    def create(cls, actor: User, user: User) -> bool:
        return actor.role == UserRole.admin

    @classmethod
    def delete(cls, actor: User, user: User) -> bool:
        return actor.role == UserRole.admin


def authorize(actor: User, policy_action, resource=None):
    if not is_authorized(actor, policy_action, resource):
        raise ForbiddenOperationError()


def is_authorized(actor: User, policy_action, resource=None) -> bool:
    return policy_action(actor, resource)
