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

from argilla.server.contexts import datasets
from argilla.server.database import get_db
from argilla.server.models import User
from argilla.server.policies import ResponsePolicyV1, authorize
from argilla.server.schemas.v1.responses import Response, ResponseUpdate
from argilla.server.security import auth

router = APIRouter(tags=["responses"])


@router.put("/responses/{response_id}", response_model=Response)
def update_response(
    *,
    db: Session = Depends(get_db),
    response_id: UUID,
    response_update: ResponseUpdate,
    current_user: User = Security(auth.get_current_user),
):
    response = datasets.get_response_by_id(db, response_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Response with id `{response_id}` not found",
        )

    authorize(current_user, ResponsePolicyV1.update(response))

    return datasets.update_response(db, response, response_update)
