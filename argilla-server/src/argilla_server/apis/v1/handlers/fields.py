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

from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.contexts import datasets
from argilla_server.database import get_async_db
from argilla_server.models import User
from argilla_server.policies import FieldPolicyV1, authorize
from argilla_server.schemas.v1.fields import Field as FieldSchema
from argilla_server.schemas.v1.fields import FieldUpdate
from argilla_server.security import auth

if TYPE_CHECKING:
    from argilla_server.models import Field

router = APIRouter(tags=["fields"])


async def _get_field(db: "AsyncSession", field_id: UUID) -> "Field":
    field = await datasets.get_field_by_id(db, field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field with id `{field_id}` not found",
        )
    return field


@router.patch("/fields/{field_id}", response_model=FieldSchema)
async def update_field(
    *,
    db: AsyncSession = Depends(get_async_db),
    field_id: UUID,
    field_update: FieldUpdate,
    current_user: User = Security(auth.get_current_user),
):
    field = await _get_field(db, field_id)

    await authorize(current_user, FieldPolicyV1.update(field))

    if field_update.settings and field_update.settings.type != field.settings["type"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Field type cannot be changed. Expected '{field.settings['type']}' but got '{field_update.settings.type}'",
        )

    return await datasets.update_field(db, field, field_update)


@router.delete("/fields/{field_id}", response_model=FieldSchema)
async def delete_field(
    *, db: AsyncSession = Depends(get_async_db), field_id: UUID, current_user: User = Security(auth.get_current_user)
):
    field = await _get_field(db, field_id)

    await authorize(current_user, FieldPolicyV1.delete(field))

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        await datasets.delete_field(db, field)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))

    return field
