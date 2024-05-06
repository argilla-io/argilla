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
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.contexts import datasets
from argilla_server.database import get_async_db
from argilla_server.models import User, VectorSettings
from argilla_server.policies import VectorSettingsPolicyV1, authorize
from argilla_server.schemas.v1.vector_settings import VectorSettings as VectorSettingsSchema
from argilla_server.schemas.v1.vector_settings import VectorSettingsUpdate
from argilla_server.security import auth

router = APIRouter(tags=["vectors-settings"])


async def _get_vector_settings(db: AsyncSession, vector_settings_id: UUID) -> VectorSettings:
    vector_settings = await datasets.get_vector_settings_by_id(db, vector_settings_id)
    if not vector_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vector settings with `{vector_settings_id}` not found",
        )
    return vector_settings


@router.patch("/vectors-settings/{vector_settings_id}", response_model=VectorSettingsSchema)
async def update_vector_settings(
    *,
    db: AsyncSession = Depends(get_async_db),
    vector_settings_id: UUID,
    vector_settings_update: VectorSettingsUpdate,
    current_user: User = Security(auth.get_current_user),
):
    vector_settings = await _get_vector_settings(db, vector_settings_id)

    await authorize(current_user, VectorSettingsPolicyV1.update(vector_settings))

    return await datasets.update_vector_settings(db, vector_settings, vector_settings_update)


@router.delete("/vectors-settings/{vector_settings_id}", response_model=VectorSettingsSchema)
async def delete_vector_settings(
    *,
    db: AsyncSession = Depends(get_async_db),
    vector_settings_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    vector_settings = await _get_vector_settings(db, vector_settings_id)

    await authorize(current_user, VectorSettingsPolicyV1.delete(vector_settings))

    return await datasets.delete_vector_settings(db, vector_settings)
