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

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from argilla_server.api.policies.v1 import DatasetPolicy, authorize
from argilla_server.api.schemas.v1.records import (
    RecordIncludeParam,
    Records,
    RecordsCreate,
    RecordsUpdate,
    SearchRecordsQuery,
    SearchRecordsResult,
)
from argilla_server.api.schemas.v1.suggestions import (
    SearchSuggestionOptions,
    SearchSuggestionOptionsQuestion,
    SearchSuggestionsOptions,
)
from argilla_server.contexts import datasets, search
from argilla_server.database import get_async_db
from argilla_server.enums import RecordSortField
from argilla_server.errors.future import UnprocessableEntityError
from argilla_server.models import Dataset, User
from argilla_server.repositories import DatasetsRepository, RecordsRepository
from argilla_server.search_engine import (
    SearchEngine,
    get_search_engine,
)
from argilla_server.security import auth
from argilla_server.services.search import SearchService
from argilla_server.telemetry import TelemetryClient, get_telemetry_client
from argilla_server.utils import parse_query_param, parse_uuids

LIST_DATASET_RECORDS_LIMIT_DEFAULT = 50
LIST_DATASET_RECORDS_LIMIT_LE = 1000
LIST_DATASET_RECORDS_DEFAULT_SORT_BY = {RecordSortField.inserted_at.value: "asc"}
DELETE_DATASET_RECORDS_LIMIT = 100

parse_record_include_param = parse_query_param(
    name="include", help="Relationships to include in the response", model=RecordIncludeParam
)

router = APIRouter()


@router.get("/datasets/{dataset_id}/records", response_model=Records, response_model_exclude_unset=True)
async def list_dataset_records(
    *,
    datasets_repository: DatasetsRepository = Depends(),
    records_repository: RecordsRepository = Depends(),
    dataset_id: UUID,
    include: Optional[RecordIncludeParam] = Depends(parse_record_include_param),
    offset: int = 0,
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, ge=1, le=LIST_DATASET_RECORDS_LIMIT_LE),
    current_user: User = Security(auth.get_current_user),
):
    dataset = await datasets_repository.get(dataset_id)
    await authorize(current_user, DatasetPolicy.list_records_with_all_responses(dataset))

    include_args = (
        dict(
            with_responses=include.with_responses,
            with_suggestions=include.with_suggestions,
            with_vectors=include.with_all_vectors or include.vectors,
        )
        if include
        else {}
    )

    records, total = await records_repository.list_by_dataset_id(
        dataset_id=dataset.id,
        offset=offset,
        limit=limit,
        **include_args,
    )

    return Records(items=records, total=total)


@router.post(
    "/datasets/{dataset_id}/records",
    status_code=status.HTTP_204_NO_CONTENT,
    deprecated=True,
    description="Deprecated in favor of POST /datasets/{dataset_id}/records/bulk",
)
async def create_dataset_records(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    dataset_id: UUID,
    records_create: RecordsCreate,
    current_user: User = Security(auth.get_current_user),
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

    await datasets.create_records(db, search_engine, dataset, records_create)

    telemetry_client.track_data(action="DatasetRecordsCreated", data={"records": len(records_create.items)})


@router.patch(
    "/datasets/{dataset_id}/records",
    status_code=status.HTTP_204_NO_CONTENT,
    deprecated=True,
    description="Deprecated in favor of PUT /datasets/{dataset_id}/records/bulk",
)
async def update_dataset_records(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    dataset_id: UUID,
    records_update: RecordsUpdate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await Dataset.get_or_raise(
        db,
        dataset_id,
        options=[
            selectinload(Dataset.fields),
            selectinload(Dataset.questions),
            selectinload(Dataset.metadata_properties),
        ],
    )

    await authorize(current_user, DatasetPolicy.update_records(dataset))

    await datasets.update_records(db, search_engine, dataset, records_update)

    telemetry_client.track_data(action="DatasetRecordsUpdated", data={"records": len(records_update.items)})


@router.delete("/datasets/{dataset_id}/records", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset_records(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
    ids: str = Query(..., description="A comma separated list with the IDs of the records to be removed"),
):
    dataset = await Dataset.get_or_raise(db, dataset_id)

    await authorize(current_user, DatasetPolicy.delete_records(dataset))

    record_ids = parse_uuids(ids)
    num_records = len(record_ids)

    if num_records == 0:
        raise UnprocessableEntityError("No record IDs provided")

    if num_records > DELETE_DATASET_RECORDS_LIMIT:
        raise UnprocessableEntityError(f"Cannot delete more than {DELETE_DATASET_RECORDS_LIMIT} records at once")

    await datasets.delete_records(db, search_engine, dataset, record_ids)


@router.post(
    "/me/datasets/{dataset_id}/records/search",
    status_code=status.HTTP_200_OK,
    response_model=SearchRecordsResult,
    response_model_exclude_unset=True,
)
async def search_current_user_dataset_records(
    *,
    datasets: DatasetsRepository = Depends(),
    db: AsyncSession = Depends(get_async_db),
    engine: SearchEngine = Depends(get_search_engine),
    dataset_id: UUID,
    body: SearchRecordsQuery,
    include: Optional[RecordIncludeParam] = Depends(parse_record_include_param),
    offset: int = Query(0, ge=0),
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, ge=1, le=LIST_DATASET_RECORDS_LIMIT_LE),
    current_user: User = Security(auth.get_current_user),
):
    dataset = await datasets.get(dataset_id)
    await authorize(current_user, DatasetPolicy.search_records(dataset))

    search_service = SearchService(
        db=db,
        engine=engine,
        records=RecordsRepository(db),
        datasets=DatasetsRepository(db),
    )

    return await search_service.search_records(
        user=current_user,
        dataset=dataset,
        search_query=body,
        offset=offset,
        limit=limit,
        include=include,
        search_bounded_to_user=True,
    )


@router.post(
    "/datasets/{dataset_id}/records/search",
    status_code=status.HTTP_200_OK,
    response_model=SearchRecordsResult,
    response_model_exclude_unset=True,
)
async def search_dataset_records(
    *,
    db: AsyncSession = Depends(get_async_db),
    engine: SearchEngine = Depends(get_search_engine),
    dataset_id: UUID,
    body: SearchRecordsQuery,
    include: Optional[RecordIncludeParam] = Depends(parse_record_include_param),
    offset: int = Query(0, ge=0),
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, ge=1, le=LIST_DATASET_RECORDS_LIMIT_LE),
    current_user: User = Security(auth.get_current_user),
):
    dataset_repository = DatasetsRepository(db)

    dataset = await dataset_repository.get(dataset_id)
    await authorize(current_user, DatasetPolicy.search_records_with_all_responses(dataset))

    search_service = SearchService(db=db, engine=engine, records=RecordsRepository(db), datasets=dataset_repository)

    return await search_service.search_records(
        user=current_user,
        dataset=dataset,
        search_query=body,
        offset=offset,
        limit=limit,
        include=include,
    )


@router.get(
    "/datasets/{dataset_id}/records/search/suggestions/options",
    status_code=status.HTTP_200_OK,
    response_model=SearchSuggestionsOptions,
)
async def list_dataset_records_search_suggestions_options(
    *,
    db: AsyncSession = Depends(get_async_db),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await Dataset.get_or_raise(db, dataset_id)

    await authorize(current_user, DatasetPolicy.search_records(dataset))

    suggestion_agents_by_question = await search.get_dataset_suggestion_agents_by_question(db, dataset.id)

    return SearchSuggestionsOptions(
        items=[
            SearchSuggestionOptions(
                question=SearchSuggestionOptionsQuestion(id=sa["question_id"], name=sa["question_name"]),
                agents=sa["suggestion_agents"],
            )
            for sa in suggestion_agents_by_question
        ]
    )
