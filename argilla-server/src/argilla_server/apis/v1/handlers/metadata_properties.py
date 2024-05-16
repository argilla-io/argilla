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
from argilla_server.models import MetadataProperty, User
from argilla_server.policies import MetadataPropertyPolicyV1, authorize
from argilla_server.schemas.v1.metadata_properties import MetadataMetrics, MetadataProperty, MetadataPropertyUpdate
from argilla_server.search_engine import SearchEngine, get_search_engine
from argilla_server.security import auth

router = APIRouter(tags=["metadata properties"])


async def _get_metadata_property(db: "AsyncSession", metadata_property_id: UUID) -> "MetadataProperty":
    metadata_property = await datasets.get_metadata_property_by_id(db, metadata_property_id)
    if not metadata_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Metadata property with id `{metadata_property_id}` not found",
        )

    return metadata_property


@router.get("/metadata-properties/{metadata_property_id}/metrics", response_model=MetadataMetrics)
async def get_metadata_property_metrics(
    *,
    db: AsyncSession = Depends(get_async_db),
    metadata_property_id: UUID,
    search_engine: SearchEngine = Depends(get_search_engine),
    current_user: User = Security(auth.get_current_user),
):
    metadata_property = await _get_metadata_property(db, metadata_property_id)

    await authorize(current_user, MetadataPropertyPolicyV1.get(metadata_property))

    return await search_engine.compute_metrics_for(metadata_property)


@router.patch("/metadata-properties/{metadata_property_id}", response_model=MetadataProperty)
async def update_metadata_property(
    *,
    db: AsyncSession = Depends(get_async_db),
    metadata_property_id: UUID,
    metadata_property_update: MetadataPropertyUpdate,
    current_user: User = Security(auth.get_current_user),
):
    metadata_property = await _get_metadata_property(db, metadata_property_id)

    await authorize(current_user, MetadataPropertyPolicyV1.update(metadata_property))

    return await datasets.update_metadata_property(db, metadata_property, metadata_property_update)


@router.delete("/metadata-properties/{metadata_property_id}", response_model=MetadataProperty)
async def delete_metadata_property(
    *,
    db: AsyncSession = Depends(get_async_db),
    metadata_property_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    metadata_property = await _get_metadata_property(db, metadata_property_id)

    await authorize(current_user, MetadataPropertyPolicyV1.delete(metadata_property))

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        await datasets.delete_metadata_property(db, metadata_property)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))

    return metadata_property
