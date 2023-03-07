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
    def list(cls, actor: User, workspace_user: WorkspaceUser):
        return True

    @classmethod
    def create(cls, actor: User, workspace_user: WorkspaceUser):
        return True

    @classmethod
    def delete(cls, actor: User, workspace_user: WorkspaceUser):
        return True


class WorkspacePolicy:
    @classmethod
    def list(cls, actor: User, workspace: Workspace):
        return True

    @classmethod
    def create(cls, actor: User, workspace: Workspace):
        # return user.is_admin
        return actor.role == UserRole.admin

    @classmethod
    def delete(cls, actor: User, workspace: Workspace):
        # return user.is_admin and workspace in user.workspaces
        return actor.role == UserRole.admin and workspace in actor.workspaces

    # Example using closures
    # @classmethod
    # def delete(cls, workspace: Workspace):
    #     return lambda user: user.role == UserRole and workspace in user.workspaces


class UserPolicy:
    @classmethod
    def whoami(cls, actor: User, user: User):
        return actor.id == user.id

    @classmethod
    def list(cls, actor: User, user: User):
        return True

    @classmethod
    def create(cls, actor: User, user: User):
        return True

    @classmethod
    def delete(cls, actor: User, user: User):
        return True


def authorize(user: User, policy_action, resource=None):
    if not is_authorized(user, policy_action, resource):
        raise ForbiddenOperationError()


def is_authorized(user: User, policy_action, resource=None):
    return policy_action(user, resource)
