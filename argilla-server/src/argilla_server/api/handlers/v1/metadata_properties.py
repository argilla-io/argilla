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

from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from argilla_server.api.policies.v1 import MetadataPropertyPolicy, authorize
from argilla_server.api.schemas.v1.metadata_properties import (
    MetadataMetrics,
    MetadataPropertyUpdate,
)
from argilla_server.api.schemas.v1.metadata_properties import (
    MetadataProperty as MetadataPropertySchema,
)
from argilla_server.contexts import datasets
from argilla_server.database import get_async_db
from argilla_server.models import MetadataProperty, User
from argilla_server.search_engine import SearchEngine, get_search_engine
from argilla_server.security import auth
from argilla_server.telemetry import TelemetryClient, get_telemetry_client

router = APIRouter(tags=["metadata properties"])


@router.get("/metadata-properties/{metadata_property_id}/metrics", response_model=MetadataMetrics)
async def get_metadata_property_metrics(
    *,
    db: AsyncSession = Depends(get_async_db),
    metadata_property_id: UUID,
    search_engine: SearchEngine = Depends(get_search_engine),
    current_user: User = Security(auth.get_current_user),
):
    metadata_property = await MetadataProperty.get_or_raise(
        db,
        metadata_property_id,
        options=[selectinload(MetadataProperty.dataset)],
    )

    await authorize(current_user, MetadataPropertyPolicy.get(metadata_property))

    return await search_engine.compute_metrics_for(metadata_property)


@router.patch("/metadata-properties/{metadata_property_id}", response_model=MetadataPropertySchema)
async def update_metadata_property(
    *,
    db: AsyncSession = Depends(get_async_db),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    metadata_property_id: UUID,
    metadata_property_update: MetadataPropertyUpdate,
    current_user: User = Security(auth.get_current_user),
):
    metadata_property = await MetadataProperty.get_or_raise(
        db,
        metadata_property_id,
        options=[selectinload(MetadataProperty.dataset)],
    )

    await authorize(current_user, MetadataPropertyPolicy.update(metadata_property))

    metadata_property = await datasets.update_metadata_property(db, metadata_property, metadata_property_update)

    await telemetry_client.track_crud_dataset_setting(
        action="update",
        setting_name="metadata_properties",
        dataset=metadata_property.dataset,
        setting=metadata_property,
    )

    return metadata_property


@router.delete("/metadata-properties/{metadata_property_id}", response_model=MetadataPropertySchema)
async def delete_metadata_property(
    *,
    db: AsyncSession = Depends(get_async_db),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    metadata_property_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    metadata_property = await MetadataProperty.get_or_raise(
        db,
        metadata_property_id,
        options=[selectinload(MetadataProperty.dataset)],
    )

    await authorize(current_user, MetadataPropertyPolicy.delete(metadata_property))

    metadata_property = await datasets.delete_metadata_property(db, metadata_property)

    await telemetry_client.track_crud_dataset_setting(
        action="delete",
        setting_name="metadata_properties",
        dataset=metadata_property.dataset,
        setting=metadata_property,
    )

    return metadata_property
