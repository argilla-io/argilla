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

from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import argilla_server.search_engine as search_engine
from argilla_server.api.policies.v1 import DatasetPolicy, RecordPolicy, authorize, is_authorized
from argilla_server.api.schemas.v1.records import (
    Filters,
    FilterScope,
    MetadataFilterScope,
    Order,
    RangeFilter,
    RecordFilterScope,
    RecordIncludeParam,
    Records,
    SearchRecord,
    SearchRecordsQuery,
    SearchRecordsResult,
    TermsFilter,
)
from argilla_server.api.schemas.v1.records import Record as RecordSchema
from argilla_server.api.schemas.v1.responses import ResponseFilterScope
from argilla_server.api.schemas.v1.suggestions import (
    SearchSuggestionOptions,
    SearchSuggestionOptionsQuestion,
    SearchSuggestionsOptions,
    SuggestionFilterScope,
)
from argilla_server.contexts import datasets, search
from argilla_server.database import get_async_db
from argilla_server.enums import RecordSortField, ResponseStatusFilter
from argilla_server.errors.future import MissingVectorError, NotFoundError, UnprocessableEntityError
from argilla_server.errors.future.base_errors import MISSING_VECTOR_ERROR_CODE
from argilla_server.models import Dataset, Field, Record, User, VectorSettings
from argilla_server.search_engine import (
    AndFilter,
    SearchEngine,
    SearchResponses,
    UserResponseStatusFilter,
    get_search_engine,
)
from argilla_server.security import auth
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


async def _filter_records_using_search_engine(
    db: "AsyncSession",
    search_engine: "SearchEngine",
    dataset: Dataset,
    limit: int,
    offset: int,
    user: Optional[User] = None,
    include: Optional[RecordIncludeParam] = None,
) -> Tuple[List[Record], int]:
    search_responses = await _get_search_responses(
        db=db,
        search_engine=search_engine,
        dataset=dataset,
        limit=limit,
        offset=offset,
        user=user,
    )

    record_ids = [response.record_id for response in search_responses.items]
    user_id = user.id if user else None

    return (
        await datasets.get_records_by_ids(
            db=db, dataset_id=dataset.id, user_id=user_id, records_ids=record_ids, include=include
        ),
        search_responses.total,
    )


def _to_search_engine_filter_scope(scope: FilterScope, user: Optional[User]) -> search_engine.FilterScope:
    if isinstance(scope, RecordFilterScope):
        return search_engine.RecordFilterScope(property=scope.property)
    elif isinstance(scope, MetadataFilterScope):
        return search_engine.MetadataFilterScope(metadata_property=scope.metadata_property)
    elif isinstance(scope, SuggestionFilterScope):
        return search_engine.SuggestionFilterScope(question=scope.question, property=scope.property)
    elif isinstance(scope, ResponseFilterScope):
        return search_engine.ResponseFilterScope(question=scope.question, property=scope.property, user=user)
    else:
        raise Exception(f"Unknown scope type {type(scope)}")


def _to_search_engine_filter(filters: Filters, user: Optional[User]) -> search_engine.Filter:
    engine_filters = []

    for filter in filters.and_:
        engine_scope = _to_search_engine_filter_scope(filter.scope, user=user)

        if isinstance(filter, TermsFilter):
            engine_filter = search_engine.TermsFilter(scope=engine_scope, values=filter.values)
        elif isinstance(filter, RangeFilter):
            engine_filter = search_engine.RangeFilter(scope=engine_scope, ge=filter.ge, le=filter.le)
        else:
            raise Exception(f"Unknown filter type {type(filter)}")

        engine_filters.append(engine_filter)

    return AndFilter(filters=engine_filters)


def _to_search_engine_sort(sort: List[Order], user: Optional[User]) -> List[search_engine.Order]:
    engine_sort = []

    for order in sort:
        engine_scope = _to_search_engine_filter_scope(order.scope, user=user)
        engine_sort.append(search_engine.Order(scope=engine_scope, order=order.order))

    return engine_sort


async def _get_search_responses(
    db: "AsyncSession",
    search_engine: "SearchEngine",
    dataset: Dataset,
    limit: int,
    offset: int,
    search_records_query: Optional[SearchRecordsQuery] = None,
    user: Optional[User] = None,
) -> "SearchResponses":
    search_records_query = search_records_query or SearchRecordsQuery()

    text_query = None
    vector_query = None
    if search_records_query.query:
        text_query = search_records_query.query.text
        vector_query = search_records_query.query.vector

    filters = search_records_query.filters
    sort = search_records_query.sort

    vector_settings = None
    record = None

    if vector_query:
        vector_settings = await VectorSettings.get_by(db, name=vector_query.name, dataset_id=dataset.id)
        if vector_settings is None:
            raise UnprocessableEntityError(f"Vector `{vector_query.name}` not found in dataset `{dataset.id}`.")

        if vector_query.record_id is not None:
            record = await Record.get_by(db, id=vector_query.record_id, dataset_id=dataset.id)
            if record is None:
                raise UnprocessableEntityError(
                    f"Record with id `{vector_query.record_id}` not found in dataset `{dataset.id}`."
                )

            await record.awaitable_attrs.vectors

            if not record.vector_value_by_vector_settings(vector_settings):
                # TODO: Once we move to v2.0 we can use here UnprocessableEntityError instead of MissingVectorError
                raise MissingVectorError(
                    message=f"Record `{record.id}` does not have a vector for vector settings `{vector_settings.name}`",
                    code=MISSING_VECTOR_ERROR_CODE,
                )

    if text_query and text_query.field and not await Field.get_by(db, name=text_query.field, dataset_id=dataset.id):
        raise UnprocessableEntityError(f"Field `{text_query.field}` not found in dataset `{dataset.id}`.")

    if vector_query and vector_settings:
        similarity_search_params = {
            "dataset": dataset,
            "vector_settings": vector_settings,
            "value": vector_query.value,
            "record": record,
            "query": text_query,
            "order": vector_query.order,
            "max_results": limit,
        }

        if filters:
            similarity_search_params["filter"] = _to_search_engine_filter(filters, user=user)

        return await search_engine.similarity_search(**similarity_search_params)
    else:
        search_params = {
            "dataset": dataset,
            "query": text_query,
            "offset": offset,
            "limit": limit,
        }

        if user is not None:
            search_params["user_id"] = user.id

        if filters:
            search_params["filter"] = _to_search_engine_filter(filters, user=user)
        if sort:
            search_params["sort"] = _to_search_engine_sort(sort, user=user)

        return await search_engine.search(**search_params)


async def _build_response_status_filter_for_search(
    response_statuses: Optional[List[ResponseStatusFilter]] = None, user: Optional[User] = None
) -> Optional[UserResponseStatusFilter]:
    user_response_status_filter = None

    if response_statuses:
        # TODO(@frascuchon): user response and status responses should be split into different filter types
        user_response_status_filter = UserResponseStatusFilter(user=user, statuses=response_statuses)

    return user_response_status_filter


async def _validate_search_records_query(db: "AsyncSession", query: SearchRecordsQuery, dataset: Dataset):
    try:
        await search.validate_search_records_query(db, query, dataset)
    except (ValueError, NotFoundError) as e:
        raise UnprocessableEntityError(str(e))


@router.get("/datasets/{dataset_id}/records", response_model=Records, response_model_exclude_unset=True)
async def list_dataset_records(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    dataset_id: UUID,
    include: Optional[RecordIncludeParam] = Depends(parse_record_include_param),
    offset: int = 0,
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, ge=1, le=LIST_DATASET_RECORDS_LIMIT_LE),
    current_user: User = Security(auth.get_current_user),
):
    dataset = await Dataset.get_or_raise(db, dataset_id)

    await authorize(current_user, DatasetPolicy.list_records_with_all_responses(dataset))

    records, total = await _filter_records_using_search_engine(
        db,
        search_engine,
        dataset=dataset,
        limit=limit,
        offset=offset,
        include=include,
    )

    return Records(items=records, total=total)


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
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    dataset_id: UUID,
    body: SearchRecordsQuery,
    include: Optional[RecordIncludeParam] = Depends(parse_record_include_param),
    offset: int = Query(0, ge=0),
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, ge=1, le=LIST_DATASET_RECORDS_LIMIT_LE),
    current_user: User = Security(auth.get_current_user),
):
    dataset = await Dataset.get_or_raise(
        db,
        dataset_id,
        options=[
            selectinload(Dataset.fields),
            selectinload(Dataset.metadata_properties),
        ],
    )

    await authorize(current_user, DatasetPolicy.search_records(dataset))

    await _validate_search_records_query(db, body, dataset)

    search_responses = await _get_search_responses(
        db=db,
        search_engine=search_engine,
        dataset=dataset,
        search_records_query=body,
        limit=limit,
        offset=offset,
        user=current_user,
    )

    record_id_score_map: Dict[UUID, Dict[str, Union[float, SearchRecord, None]]] = {
        response.record_id: {"query_score": response.score, "search_record": None}
        for response in search_responses.items
    }

    records = await datasets.get_records_by_ids(
        db=db,
        dataset_id=dataset_id,
        records_ids=list(record_id_score_map.keys()),
        include=include,
        user_id=current_user.id,
    )

    for record in records:
        record.dataset = dataset
        record.metadata_ = await _filter_record_metadata_for_user(record, current_user)

        record_id_score_map[record.id]["search_record"] = SearchRecord(
            record=RecordSchema.from_orm(record),
            query_score=record_id_score_map[record.id]["query_score"],
        )

    return SearchRecordsResult(
        items=[record["search_record"] for record in record_id_score_map.values()],
        total=search_responses.total,
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
    search_engine: SearchEngine = Depends(get_search_engine),
    dataset_id: UUID,
    body: SearchRecordsQuery,
    include: Optional[RecordIncludeParam] = Depends(parse_record_include_param),
    offset: int = Query(0, ge=0),
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, ge=1, le=LIST_DATASET_RECORDS_LIMIT_LE),
    current_user: User = Security(auth.get_current_user),
):
    dataset = await Dataset.get_or_raise(db, dataset_id, options=[selectinload(Dataset.fields)])

    await authorize(current_user, DatasetPolicy.search_records_with_all_responses(dataset))

    await _validate_search_records_query(db, body, dataset)

    search_responses = await _get_search_responses(
        db=db,
        search_engine=search_engine,
        dataset=dataset,
        search_records_query=body,
        limit=limit,
        offset=offset,
    )

    record_id_score_map = {
        response.record_id: {"query_score": response.score, "search_record": None}
        for response in search_responses.items
    }

    records = await datasets.get_records_by_ids(
        db=db,
        dataset_id=dataset_id,
        records_ids=list(record_id_score_map.keys()),
        include=include,
    )

    for record in records:
        record_id_score_map[record.id]["search_record"] = SearchRecord(
            record=RecordSchema.from_orm(record),
            query_score=record_id_score_map[record.id]["query_score"],
        )

    return SearchRecordsResult(
        items=[record["search_record"] for record in record_id_score_map.values()],
        total=search_responses.total,
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


async def _filter_record_metadata_for_user(record: Record, user: User) -> Optional[Dict[str, Any]]:
    if record.metadata_ is None:
        return None

    metadata = {}
    for metadata_name in list(record.metadata_.keys()):
        if await is_authorized(user, RecordPolicy.get_metadata(record, metadata_name)):
            metadata[metadata_name] = record.metadata_[metadata_name]
    return metadata
