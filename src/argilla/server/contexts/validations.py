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

from argilla.server.contexts import accounts
from argilla.server.database import SessionLocal
from argilla.server.errors import EntityNotFoundError, ForbiddenOperationError
from argilla.server.models import User, Workspace


def validate_workspaces_user_access(user: User, *workspaces: Workspace):
    for workspace in workspaces:
        if workspace in user.workspaces:
            continue
        elif accounts.is_superuser(user):
            continue
        else:
            raise ForbiddenOperationError(f"Cannot access workspace {workspace}")
    return True


def validate_and_get_workspace_by_name(db: SessionLocal, workspace_name: str) -> Workspace:
    workspace = accounts.get_workspace_by_name(db, workspace_name)
    if not workspace:
        raise EntityNotFoundError(name=workspace_name, type=Workspace)
    return workspace
