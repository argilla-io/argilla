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
from enum import Enum

from argilla.server.models import User, UserRole, Workspace


class Permission(Enum):
    create = 1
    read = 2
    update = 3
    delete = 4


def _allow_workspace_create(user: User, workspace: Workspace) -> bool:
    return user.role == UserRole.admin


def _is_allowed_read_workspace(user: User, workspace: Workspace) -> bool:
    return user.role == UserRole.admin or workspace in user.workspaces


def _is_allowed_update_workspace(user: User, workspace: Workspace) -> bool:
    return _is_allowed_read_workspace(user, workspace)


def _is_allowed_delete_workspace(user: User, workspace: Workspace) -> bool:
    return _is_allowed_read_workspace(user, workspace)


def is_authorized(user: User, permission: Permission, workspace: Workspace):
    if permission == Permission.read:
        return _is_allowed_read_workspace(user, workspace)
    elif permission == Permission.create:
        return _allow_workspace_create(user, workspace)
    elif permission == Permission.update:
        return _is_allowed_update_workspace(user, workspace)
    elif permission == Permission.delete:
        return _is_allowed_delete_workspace(user, workspace)
    else:
        return False
