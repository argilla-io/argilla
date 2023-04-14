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
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.orm import Session

from argilla.server.contexts import datasets
from argilla.server.database import get_db
from argilla.server.policies import RecordPolicyV1, authorize
from argilla.server.schemas.v1.records import (
    Record,
    RecordInclude,
    RecordsCreate,
    RecordsList,
    Response,
)
from argilla.server.security import auth
from argilla.server.security.model import User

router = APIRouter(tags=["records"])


def _get_dataset(db: Session, dataset_id: UUID):
    dataset = datasets.get_dataset_by_id(db, dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with id `{dataset_id}` not found",
        )

    return dataset


@router.get("/datasets/{dataset_id}/records", response_model=RecordsList)
def list_records(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    offset: int = 0,
    limit: int = Query(default=50, lte=1000),
    include: Optional[List[RecordInclude]] = Query(None),
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, RecordPolicyV1.get(dataset))

    records = datasets.list_records(db, dataset, offset=offset, limit=limit)

    for record in records:
        record_schema = Record(id=record.id, fields=record.fields)
        if RecordInclude.responses in include:
            # TODO: Move this to context, please
            response = db.query(Response).filter_by(record_id=record.id, user_id=current_user.id).first()
            if response:
                record_schema.responses = {current_user.username: response.values}

    return RecordsList(total=0, items=records)


@router.put("/records/{record_id}/responses", response_model=Response)
def update_record_responses(
    *,
    db: Session = Depends(get_db),
    record_id: UUID,
    response: Response,
    current_user: User = Security(auth.get_current_user),
):
    record = datasets.get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with id `{record_id}` not found",
        )

    authorize(current_user, RecordPolicyV1.update_response(record))

    datasets.create_or_update_response(db, record, current_user, response_create_or_update=response)

    return response
