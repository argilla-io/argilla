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

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from argilla_server.api.policies.v1 import DatasetPolicy, MetadataPropertyPolicy, authorize, is_authorized
from argilla_server.api.schemas.v1.datasets import (
    Dataset as DatasetSchema,
)
from argilla_server.api.schemas.v1.datasets import (
    DatasetCreate,
    DatasetMetrics,
    DatasetProgress,
    Datasets,
    DatasetUpdate,
)
from argilla_server.api.schemas.v1.fields import Field, FieldCreate, Fields
from argilla_server.api.schemas.v1.metadata_properties import (
    MetadataProperties,
    MetadataProperty,
    MetadataPropertyCreate,
)
from argilla_server.api.schemas.v1.vector_settings import VectorSettings, VectorSettingsCreate, VectorsSettings
from argilla_server.contexts import datasets
from argilla_server.database import get_async_db
from argilla_server.enums import ResponseStatus
from argilla_server.models import Dataset, User
from argilla_server.search_engine import (
    SearchEngine,
    get_search_engine,
)
from argilla_server.security import auth
from argilla_server.telemetry import TelemetryClient, get_telemetry_client

router = APIRouter()


async def _filter_metadata_properties_by_policy(
    current_user: User, metadata_properties: List[MetadataProperty]
) -> List[MetadataProperty]:
    filtered_metadata_properties = []

    for metadata_property in metadata_properties:
        metadata_property_is_authorized = await is_authorized(
            current_user, MetadataPropertyPolicy.get(metadata_property)
        )

        if metadata_property_is_authorized:
            filtered_metadata_properties.append(metadata_property)

    return filtered_metadata_properties


@router.get("/me/datasets", response_model=Datasets)
async def list_current_user_datasets(
    *,
    db: AsyncSession = Depends(get_async_db),
    workspace_id: Optional[UUID] = None,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, DatasetPolicy.list(workspace_id))

    if not workspace_id:
        if current_user.is_owner:
            dataset_list = await datasets.list_datasets(db)
        else:
            await current_user.awaitable_attrs.datasets
            dataset_list = current_user.datasets
    else:
        dataset_list = await datasets.list_datasets_by_workspace_id(db, workspace_id)

    return Datasets(items=dataset_list)


@router.get("/datasets/{dataset_id}/fields", response_model=Fields)
async def list_dataset_fields(
    *, db: AsyncSession = Depends(get_async_db), dataset_id: UUID, current_user: User = Security(auth.get_current_user)
):
    dataset = await Dataset.get_or_raise(db, dataset_id, options=[selectinload(Dataset.fields)])

    await authorize(current_user, DatasetPolicy.get(dataset))

    return Fields(items=dataset.fields)


@router.get("/datasets/{dataset_id}/vectors-settings", response_model=VectorsSettings)
async def list_dataset_vector_settings(
    *, db: AsyncSession = Depends(get_async_db), dataset_id: UUID, current_user: User = Security(auth.get_current_user)
):
    dataset = await Dataset.get_or_raise(db, dataset_id, options=[selectinload(Dataset.vectors_settings)])

    await authorize(current_user, DatasetPolicy.get(dataset))

    return VectorsSettings(items=dataset.vectors_settings)


@router.get("/me/datasets/{dataset_id}/metadata-properties", response_model=MetadataProperties)
async def list_current_user_dataset_metadata_properties(
    *, db: AsyncSession = Depends(get_async_db), dataset_id: UUID, current_user: User = Security(auth.get_current_user)
):
    dataset = await Dataset.get_or_raise(db, dataset_id, options=[selectinload(Dataset.metadata_properties)])

    await authorize(current_user, DatasetPolicy.get(dataset))

    filtered_metadata_properties = await _filter_metadata_properties_by_policy(
        current_user, dataset.metadata_properties
    )

    return MetadataProperties(items=filtered_metadata_properties)


@router.get("/datasets/{dataset_id}", response_model=DatasetSchema)
async def get_dataset(
    *, db: AsyncSession = Depends(get_async_db), dataset_id: UUID, current_user: User = Security(auth.get_current_user)
):
    dataset = await Dataset.get_or_raise(db, dataset_id)

    await authorize(current_user, DatasetPolicy.get(dataset))

    return dataset


@router.get("/me/datasets/{dataset_id}/metrics", response_model=DatasetMetrics)
async def get_current_user_dataset_metrics(
    *,
    db: AsyncSession = Depends(get_async_db),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await Dataset.get_or_raise(db, dataset_id)

    await authorize(current_user, DatasetPolicy.get(dataset))

    return {
        "records": {
            "count": await datasets.count_records_by_dataset_id(db, dataset_id),
        },
        "responses": {
            "count": await datasets.count_responses_by_dataset_id_and_user_id(db, dataset_id, current_user.id),
            "submitted": await datasets.count_responses_by_dataset_id_and_user_id(
                db, dataset_id, current_user.id, ResponseStatus.submitted
            ),
            "discarded": await datasets.count_responses_by_dataset_id_and_user_id(
                db, dataset_id, current_user.id, ResponseStatus.discarded
            ),
            "draft": await datasets.count_responses_by_dataset_id_and_user_id(
                db, dataset_id, current_user.id, ResponseStatus.draft
            ),
        },
    }


@router.get("/datasets/{dataset_id}/progress", response_model=DatasetProgress)
async def get_dataset_progress(
    *,
    db: AsyncSession = Depends(get_async_db),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await Dataset.get_or_raise(db, dataset_id)

    await authorize(current_user, DatasetPolicy.get(dataset))

    return await datasets.get_dataset_progress(db, dataset_id)


@router.post("/datasets", status_code=status.HTTP_201_CREATED, response_model=DatasetSchema)
async def create_dataset(
    *,
    db: AsyncSession = Depends(get_async_db),
    dataset_create: DatasetCreate,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, DatasetPolicy.create(dataset_create.workspace_id))

    return await datasets.create_dataset(db, dataset_create)


@router.post("/datasets/{dataset_id}/fields", status_code=status.HTTP_201_CREATED, response_model=Field)
async def create_dataset_field(
    *,
    db: AsyncSession = Depends(get_async_db),
    dataset_id: UUID,
    field_create: FieldCreate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await Dataset.get_or_raise(db, dataset_id)

    await authorize(current_user, DatasetPolicy.create_field(dataset))

    return await datasets.create_field(db, dataset, field_create)


@router.post(
    "/datasets/{dataset_id}/metadata-properties", status_code=status.HTTP_201_CREATED, response_model=MetadataProperty
)
async def create_dataset_metadata_property(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    dataset_id: UUID,
    metadata_property_create: MetadataPropertyCreate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await Dataset.get_or_raise(db, dataset_id)

    await authorize(current_user, DatasetPolicy.create_metadata_property(dataset))

    return await datasets.create_metadata_property(db, search_engine, dataset, metadata_property_create)


@router.post(
    "/datasets/{dataset_id}/vectors-settings", status_code=status.HTTP_201_CREATED, response_model=VectorSettings
)
async def create_dataset_vector_settings(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    dataset_id: UUID,
    vector_settings_create: VectorSettingsCreate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await Dataset.get_or_raise(db, dataset_id)

    await authorize(current_user, DatasetPolicy.create_vector_settings(dataset))

    return await datasets.create_vector_settings(db, search_engine, dataset, vector_settings_create)


@router.put("/datasets/{dataset_id}/publish", response_model=DatasetSchema)
async def publish_dataset(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
) -> Dataset:
    dataset = await Dataset.get_or_raise(
        db,
        dataset_id,
        options=[
            selectinload(Dataset.fields),
            selectinload(Dataset.questions),
            selectinload(Dataset.metadata_properties),
            selectinload(Dataset.vectors_settings),
        ],
    )

    await authorize(current_user, DatasetPolicy.publish(dataset))

    dataset = await datasets.publish_dataset(db, search_engine, dataset)

    telemetry_client.track_data(
        action="PublishedDataset",
        data={"questions": list(set([question.settings["type"] for question in dataset.questions]))},
    )

    return dataset


@router.delete("/datasets/{dataset_id}", response_model=DatasetSchema)
async def delete_dataset(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await Dataset.get_or_raise(db, dataset_id)

    await authorize(current_user, DatasetPolicy.delete(dataset))

    return await datasets.delete_dataset(db, search_engine, dataset)


@router.patch("/datasets/{dataset_id}", response_model=DatasetSchema)
async def update_dataset(
    *,
    db: AsyncSession = Depends(get_async_db),
    dataset_id: UUID,
    dataset_update: DatasetUpdate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await Dataset.get_or_raise(db, dataset_id)

    await authorize(current_user, DatasetPolicy.update(dataset))

    return await datasets.update_dataset(db, dataset, dataset_update)
