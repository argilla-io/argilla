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
from argilla.server.schemas.v1.records import Response, ResponseCreate
from argilla.server.search_engine import SearchEngine, get_search_engine
from argilla.server.security import auth

router = APIRouter(tags=["records"])


@router.post("/records/{record_id}/responses", status_code=status.HTTP_201_CREATED, response_model=Response)
async def create_record_response(
    *,
    db: Session = Depends(get_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    record_id: UUID,
    response_create: ResponseCreate,
    current_user: User = Security(auth.get_current_user),
):
    record = datasets.get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with id `{record_id}` not found",
        )

    authorize(current_user, RecordPolicyV1.create_response(record))

    if datasets.get_response_by_record_id_and_user_id(db, record_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Response already exists for record with id `{record_id}` and by user with id `{current_user.id}`",
        )

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        return await datasets.create_response(db, search_engine, record, current_user, response_create)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
