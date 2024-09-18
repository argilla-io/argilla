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
from starlette import status

from argilla_server.api.policies.v1 import DatasetPolicy, authorize
from argilla_server.api.schemas.v1.records_bulk import RecordsBulk, RecordsBulkCreate, RecordsBulkUpsert
from argilla_server.bulk.records_bulk import CreateRecordsBulk, UpsertRecordsBulk
from argilla_server.database import get_async_db
from argilla_server.models import Dataset, User
from argilla_server.search_engine import SearchEngine, get_search_engine
from argilla_server.security import auth
from argilla_server.telemetry import TelemetryClient, get_telemetry_client

router = APIRouter()


@router.post(
    "/datasets/{dataset_id}/records/bulk",
    response_model=RecordsBulk,
    status_code=status.HTTP_201_CREATED,
)
async def create_dataset_records_bulk(
    *,
    dataset_id: UUID,
    records_bulk_create: RecordsBulkCreate,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    current_user: User = Security(auth.get_current_user),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
):
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

    await authorize(current_user, DatasetPolicy.create_records(dataset))

    records_bulk = await CreateRecordsBulk(db, search_engine).create_records_bulk(dataset, records_bulk_create)

    return records_bulk


@router.put("/datasets/{dataset_id}/records/bulk", response_model=RecordsBulk)
async def upsert_dataset_records_bulk(
    *,
    dataset_id: UUID,
    records_bulk_create: RecordsBulkUpsert,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    current_user: User = Security(auth.get_current_user),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
):
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

    await authorize(current_user, DatasetPolicy.upsert_records(dataset))

    records_bulk = await UpsertRecordsBulk(db, search_engine).upsert_records_bulk(dataset, records_bulk_create)

    updated = len(records_bulk.updated_item_ids)
    created = len(records_bulk.items) - updated

    return records_bulk
