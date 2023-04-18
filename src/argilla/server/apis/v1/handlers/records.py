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
from argilla.server.policies import RecordPolicyV1, authorize
from argilla.server.schemas.v1.records import Response, ResponseCreate, Responses
from argilla.server.security import auth

router = APIRouter(tags=["records"])


def _get_record(db: Session, record_id: UUID):
    record = datasets.get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with id `{record_id}` not found",
        )
    return record


@router.get("/records/{record_id}/responses", response_model=Responses)
def list_record_responses(
    *,
    db: Session = Depends(get_db),
    record_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    record = _get_record(db, record_id)

    authorize(current_user, RecordPolicyV1.get(record))

    if current_user.is_admin:
        return Responses(items=datasets.list_responses_by_record_id(db, record.id))
    else:
        return Responses(items=[datasets.get_response_by_record_id_and_user_id(db, record.id, current_user.id)])


@router.post("/records/{record_id}/responses", status_code=status.HTTP_201_CREATED, response_model=Response)
def create_record_response(
    *,
    db: Session = Depends(get_db),
    record_id: UUID,
    response_create: ResponseCreate,
    current_user: User = Security(auth.get_current_user),
):
    record = _get_record(db, record_id)

    authorize(current_user, RecordPolicyV1.create_response(record))

    if datasets.get_response_by_record_id_and_user_id(db, record_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Response already exists for record with id `{record_id}` and by user with id `{current_user.id}`",
        )

    return datasets.create_response(db, record, current_user, response_create)
