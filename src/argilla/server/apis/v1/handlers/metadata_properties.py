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

from argilla.server.contexts import datasets
from argilla.server.database import get_async_db
from argilla.server.models import MetadataProperty, User
from argilla.server.policies import MetadataPropertyPolicyV1, authorize
from argilla.server.schemas.v1.metadata_properties import MetadataMetrics
from argilla.server.search_engine import SearchEngine, get_search_engine
from argilla.server.security import auth

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

    await authorize(current_user, MetadataPropertyPolicyV1.compute_metrics(metadata_property))

    return await search_engine.compute_metrics_for(metadata_property)
