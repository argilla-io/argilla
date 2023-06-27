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

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from argilla.server.contexts import accounts
from argilla.server.database import get_db
from argilla.server.policies import WorkspacePolicyV1, authorize
from argilla.server.schemas.v1.workspaces import Workspace
from argilla.server.security import auth
from argilla.server.security.model import User

router = APIRouter(tags=["workspaces"])


@router.get("/workspaces/{workspace_id}", response_model=Workspace)
def get_workspace(
    *,
    db: Session = Depends(get_db),
    workspace_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    authorize(current_user, WorkspacePolicyV1.get(workspace_id))

    workspace = accounts.get_workspace_by_id(db, workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with id `{workspace_id}` not found",
        )

    return workspace
