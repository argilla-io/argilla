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

import re
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

import argilla.server.errors.future as errors
from argilla.server.apis.v1.handlers.datasets.datasets import _get_dataset
from argilla.server.contexts import datasets, search
from argilla.server.database import get_async_db
from argilla.server.enums import MetadataPropertyType, RecordSortField, ResponseStatusFilter, SortOrder
from argilla.server.models import Dataset as DatasetModel
from argilla.server.models import Record, User
from argilla.server.policies import DatasetPolicyV1, authorize
from argilla.server.schemas.v1.datasets import (
    Dataset,
    Filters,
    FilterScope,
    MetadataFilterScope,
    MetadataParsedQueryParam,
    MetadataQueryParams,
    Order,
    RangeFilter,
    RecordFilterScope,
    RecordIncludeParam,
    Records,
    RecordsCreate,
    RecordsUpdate,
    ResponseFilterScope,
    SearchRecord,
    SearchRecordsQuery,
    SearchRecordsResult,
    SearchSuggestionOptions,
    SearchSuggestionOptionsQuestion,
    SearchSuggestionsOptions,
    SuggestionFilterScope,
    TermsFilter,
    VectorSettings,
)
from argilla.server.schemas.v1.datasets import (
    Record as RecordSchema,
)
from argilla.server.search_engine import (
    AndFilter,
    FloatMetadataFilter,
    IntegerMetadataFilter,
    MetadataFilter,
    SearchEngine,
    SearchResponses,
    SortBy,
    TermsMetadataFilter,
    UserResponseStatusFilter,
    get_search_engine,
)
from argilla.server.search_engine import (
    Filter as SearchEngineFilter,
)
from argilla.server.search_engine import (
    FilterScope as SearchEngineFilterScope,
)
from argilla.server.search_engine import (
    MetadataFilterScope as SearchEngineMetadataFilterScope,
)
from argilla.server.search_engine import (
    Order as SearchEngineOrder,
)
from argilla.server.search_engine import (
    RangeFilter as SearchEngineRangeFilter,
)
from argilla.server.search_engine import (
    RecordFilterScope as SearchEngineRecordFilterScope,
)
from argilla.server.search_engine import (
    ResponseFilterScope as SearchEngineResponseFilterScope,
)
from argilla.server.search_engine import (
    SuggestionFilterScope as SearchEngineSuggestionFilterScope,
)
from argilla.server.search_engine import (
    TermsFilter as SearchEngineTermsFilter,
)
from argilla.server.security import auth
from argilla.server.utils import parse_query_param, parse_uuids
from argilla.utils.telemetry import TelemetryClient, get_telemetry_client

LIST_DATASET_RECORDS_LIMIT_DEFAULT = 50
LIST_DATASET_RECORDS_LIMIT_LE = 1000
LIST_DATASET_RECORDS_DEFAULT_SORT_BY = {RecordSortField.inserted_at.value: "asc"}
DELETE_DATASET_RECORDS_LIMIT = 100

_RECORD_SORT_FIELD_VALUES = tuple(field.value for field in RecordSortField)
_VALID_SORT_VALUES = tuple(sort.value for sort in SortOrder)
_METADATA_PROPERTY_SORT_BY_REGEX = re.compile(r"^metadata\.(?P<name>(?=.*[a-z0-9])[a-z0-9_-]+)$")


SortByQueryParamParsed = Annotated[
    Dict[str, str],
    Depends(
        parse_query_param(
            name="sort_by",
            description=(
                "The field used to sort the records. Expected format is `field` or `field:{asc,desc}`, where `field`"
                " can be 'inserted_at', 'updated_at' or the name of a metadata property"
            ),
            max_values_per_key=1,
            group_keys_without_values=False,
        )
    ),
]

parse_record_include_param = parse_query_param(
    name="include", help="Relationships to include in the response", model=RecordIncludeParam
)

router = APIRouter()


async def _filter_records_using_search_engine(
    db: "AsyncSession",
    search_engine: "SearchEngine",
    dataset: Dataset,
    parsed_metadata: List[MetadataParsedQueryParam],
    limit: int,
    offset: int,
    user: Optional[User] = None,
    response_statuses: Optional[List[ResponseStatusFilter]] = None,
    include: Optional[RecordIncludeParam] = None,
    sort_by_query_param: Optional[Dict[str, str]] = None,
) -> Tuple[List["Record"], int]:
    search_responses = await _get_search_responses(
        db=db,
        search_engine=search_engine,
        dataset=dataset,
        limit=limit,
        offset=offset,
        user=user,
        parsed_metadata=parsed_metadata,
        response_statuses=response_statuses,
        sort_by_query_param=sort_by_query_param,
    )

    record_ids = [response.record_id for response in search_responses.items]
    user_id = user.id if user else None

    return (
        await datasets.get_records_by_ids(
            db=db, dataset_id=dataset.id, user_id=user_id, records_ids=record_ids, include=include
        ),
        search_responses.total,
    )


def _to_search_engine_scope(scope: FilterScope, user: Optional[User]) -> SearchEngineFilterScope:
    if isinstance(scope, RecordFilterScope):
        return SearchEngineRecordFilterScope(property=scope.property)
    elif isinstance(scope, MetadataFilterScope):
        return SearchEngineMetadataFilterScope(metadata_property=scope.metadata_property)
    elif isinstance(scope, SuggestionFilterScope):
        return SearchEngineSuggestionFilterScope(question=scope.question, property=scope.property)
    elif isinstance(scope, ResponseFilterScope):
        return SearchEngineResponseFilterScope(question=scope.question, property=scope.property, user=user)
    else:
        raise Exception(f"Unknown scope type {type(scope)}")


def _to_search_engine_filter(filters: Filters, user: Optional[User]) -> SearchEngineFilter:
    engine_filters = []

    for filter in filters.and_:
        engine_scope = _to_search_engine_scope(filter.scope, user=user)

        if isinstance(filter, TermsFilter):
            engine_filter = SearchEngineTermsFilter(scope=engine_scope, values=filter.values)
        elif isinstance(filter, RangeFilter):
            engine_filter = SearchEngineRangeFilter(scope=engine_scope, ge=filter.ge, le=filter.le)
        else:
            raise Exception(f"Unknown filter type {type(filter)}")

        engine_filters.append(engine_filter)

    return AndFilter(filters=engine_filters)


def _to_search_engine_sort(sort: List[Order], user: Optional[User]) -> List[SearchEngineOrder]:
    engine_sort = []

    for order in sort:
        engine_scope = _to_search_engine_scope(order.scope, user=user)
        engine_sort.append(SearchEngineOrder(scope=engine_scope, order=order.order))

    return engine_sort


async def _get_search_responses(
    db: "AsyncSession",
    search_engine: "SearchEngine",
    dataset: DatasetModel,
    parsed_metadata: List[MetadataParsedQueryParam],
    limit: int,
    offset: int,
    search_records_query: Optional[SearchRecordsQuery] = None,
    user: Optional[User] = None,
    response_statuses: Optional[List[ResponseStatusFilter]] = None,
    sort_by_query_param: Optional[Dict[str, str]] = None,
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
        vector_settings = await _get_vector_settings_by_name_or_raise(db, dataset, vector_query.name)
        if vector_query.record_id is not None:
            record = await _get_dataset_record_by_id_or_raise(db, dataset, vector_query.record_id)
            await record.awaitable_attrs.vectors

            if not record.vector_value_by_vector_settings(vector_settings):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Record `{record.id}` does not have a vector for vector settings `{vector_settings.name}`",
                )

    if (
        text_query
        and text_query.field
        and not await datasets.get_field_by_name_and_dataset_id(db, text_query.field, dataset.id)
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Field `{text_query.field}` not found in dataset `{dataset.id}`.",
        )

    metadata_filters = await _build_metadata_filters(db, dataset, parsed_metadata)
    response_status_filter = await _build_response_status_filter_for_search(response_statuses, user=user)
    sort_by = await _build_sort_by(db, dataset, sort_by_query_param)

    if vector_query and vector_settings:
        similarity_search_params = {
            "dataset": dataset,
            "vector_settings": vector_settings,
            "value": vector_query.value,
            "record": record,
            "query": text_query,
            "order": vector_query.order,
            "metadata_filters": metadata_filters,
            "user_response_status_filter": response_status_filter,
            "max_results": limit,
        }

        if filters:
            similarity_search_params["filter"] = _to_search_engine_filter(filters, user=user)

        return await search_engine.similarity_search(**similarity_search_params)
    else:
        search_params = {
            "dataset": dataset,
            "query": text_query,
            "metadata_filters": metadata_filters,
            "user_response_status_filter": response_status_filter,
            "offset": offset,
            "limit": limit,
            "sort_by": sort_by,
        }

        if filters:
            search_params["filter"] = _to_search_engine_filter(filters, user=user)
        if sort:
            search_params["sort"] = _to_search_engine_sort(sort, user=user)

        return await search_engine.search(**search_params)


async def _build_metadata_filters(
    db: "AsyncSession", dataset: Dataset, parsed_metadata: List[MetadataParsedQueryParam]
) -> List["MetadataFilter"]:
    try:
        metadata_filters = []
        for metadata_param in parsed_metadata:
            metadata_property = await datasets.get_metadata_property_by_name_and_dataset_id(
                db, name=metadata_param.name, dataset_id=dataset.id
            )
            if metadata_property is None:
                continue  # won't fail on unknown metadata filter name

            if metadata_property.type == MetadataPropertyType.terms:
                metadata_filter_class = TermsMetadataFilter
            elif metadata_property.type == MetadataPropertyType.integer:
                metadata_filter_class = IntegerMetadataFilter
            elif metadata_property.type == MetadataPropertyType.float:
                metadata_filter_class = FloatMetadataFilter
            else:
                raise ValueError(f"Not found filter for type {metadata_property.type}")

            metadata_filters.append(metadata_filter_class.from_string(metadata_property, metadata_param.value))
    except ValueError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Cannot parse provided metadata filters: {ex}"
        )
    return metadata_filters


async def _build_response_status_filter_for_search(
    response_statuses: Optional[List[ResponseStatusFilter]] = None, user: Optional[User] = None
) -> Optional[UserResponseStatusFilter]:
    user_response_status_filter = None

    if response_statuses:
        # TODO(@frascuchon): user response and status responses should be split into different filter types
        user_response_status_filter = UserResponseStatusFilter(user=user, statuses=response_statuses)

    return user_response_status_filter


async def _build_sort_by(
    db: "AsyncSession", dataset: Dataset, sort_by_query_param: Optional[Dict[str, str]] = None
) -> Union[List[SortBy], None]:
    if sort_by_query_param is None:
        return None

    sorts_by = []
    for sort_field, sort_order in sort_by_query_param.items():
        if sort_field in _RECORD_SORT_FIELD_VALUES:
            field = sort_field
        elif (match := _METADATA_PROPERTY_SORT_BY_REGEX.match(sort_field)) is not None:
            metadata_property_name = match.group("name")
            metadata_property = await datasets.get_metadata_property_by_name_and_dataset_id(
                db, name=metadata_property_name, dataset_id=dataset.id
            )
            if not metadata_property:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        f"Provided metadata property in 'sort_by' query param '{metadata_property_name}' not found in"
                        f" dataset with '{dataset.id}'."
                    ),
                )
            field = metadata_property
        else:
            valid_sort_fields = ", ".join(f"'{sort_field}'" for sort_field in _RECORD_SORT_FIELD_VALUES)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Provided sort field in 'sort_by' query param '{sort_field}' is not valid. It must be either"
                    f" {valid_sort_fields} or `metadata.metadata-property-name`"
                ),
            )

        if sort_order is not None and sort_order not in _VALID_SORT_VALUES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Provided sort order in 'sort_by' query param '{sort_order}' for field '{sort_field}' is not"
                    " valid."
                ),
            )

        sorts_by.append(SortBy(field=field, order=sort_order or SortOrder.asc.value))

    return sorts_by


async def _validate_search_records_query(db: "AsyncSession", query: SearchRecordsQuery, dataset_id: UUID):
    try:
        await search.validate_search_records_query(db, query, dataset_id)
    except (ValueError, errors.NotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


async def _get_dataset_record_by_id_or_raise(db: "AsyncSession", dataset: Dataset, record_id: UUID) -> "Record":
    record = await datasets.get_record_by_id(db, record_id)
    if record is None or record.dataset_id != dataset.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Record with id `{record_id}` not found in dataset `{dataset.id}`.",
        )

    return record


async def _get_vector_settings_by_name_or_raise(
    db: "AsyncSession", dataset: Dataset, vector_name: str
) -> VectorSettings:
    vector_settings = await datasets.get_vector_settings_by_name_and_dataset_id(
        db, name=vector_name, dataset_id=dataset.id
    )

    if vector_settings is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Vector `{vector_name}` not found in dataset `{dataset.id}`.",
        )

    return vector_settings


@router.get("/me/datasets/{dataset_id}/records", response_model=Records, response_model_exclude_unset=True)
async def list_current_user_dataset_records(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    dataset_id: UUID,
    metadata: MetadataQueryParams = Depends(),
    sort_by_query_param: SortByQueryParamParsed,
    include: Optional[RecordIncludeParam] = Depends(parse_record_include_param),
    response_statuses: List[ResponseStatusFilter] = Query([], alias="response_status"),
    offset: int = 0,
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, ge=1, le=LIST_DATASET_RECORDS_LIMIT_LE),
    current_user: User = Security(auth.get_current_user),
):
    dataset = await _get_dataset(db, dataset_id)

    await authorize(current_user, DatasetPolicyV1.get(dataset))

    records, total = await _filter_records_using_search_engine(
        db,
        search_engine,
        dataset=dataset,
        parsed_metadata=metadata.metadata_parsed,
        limit=limit,
        offset=offset,
        user=current_user,
        response_statuses=response_statuses,
        include=include,
        sort_by_query_param=sort_by_query_param or LIST_DATASET_RECORDS_DEFAULT_SORT_BY,
    )

    return Records(items=records, total=total)


@router.get("/datasets/{dataset_id}/records", response_model=Records, response_model_exclude_unset=True)
async def list_dataset_records(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    dataset_id: UUID,
    metadata: MetadataQueryParams = Depends(),
    sort_by_query_param: SortByQueryParamParsed,
    include: Optional[RecordIncludeParam] = Depends(parse_record_include_param),
    response_statuses: List[ResponseStatusFilter] = Query([], alias="response_status"),
    offset: int = 0,
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, ge=1, le=LIST_DATASET_RECORDS_LIMIT_LE),
    current_user: User = Security(auth.get_current_user),
):
    dataset = await _get_dataset(db, dataset_id)

    await authorize(current_user, DatasetPolicyV1.list_records_with_all_responses(dataset))

    records, total = await _filter_records_using_search_engine(
        db,
        search_engine,
        dataset=dataset,
        parsed_metadata=metadata.metadata_parsed,
        limit=limit,
        offset=offset,
        response_statuses=response_statuses,
        include=include,
        sort_by_query_param=sort_by_query_param or LIST_DATASET_RECORDS_DEFAULT_SORT_BY,
    )

    return Records(items=records, total=total)


@router.post("/datasets/{dataset_id}/records", status_code=status.HTTP_204_NO_CONTENT)
async def create_dataset_records(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    dataset_id: UUID,
    records_create: RecordsCreate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await _get_dataset(
        db, dataset_id, with_fields=True, with_questions=True, with_metadata_properties=True, with_vectors_settings=True
    )

    await authorize(current_user, DatasetPolicyV1.create_records(dataset))

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    #  After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        await datasets.create_records(db, search_engine, dataset=dataset, records_create=records_create)
        telemetry_client.track_data(action="DatasetRecordsCreated", data={"records": len(records_create.items)})
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.patch("/datasets/{dataset_id}/records", status_code=status.HTTP_204_NO_CONTENT)
async def update_dataset_records(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    dataset_id: UUID,
    records_update: RecordsUpdate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await _get_dataset(db, dataset_id, with_fields=True, with_questions=True, with_metadata_properties=True)

    await authorize(current_user, DatasetPolicyV1.update_records(dataset))

    try:
        await datasets.update_records(db, search_engine, dataset, records_update)
        telemetry_client.track_data(action="DatasetRecordsUpdated", data={"records": len(records_update.items)})
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.delete("/datasets/{dataset_id}/records", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset_records(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
    ids: str = Query(..., description="A comma separated list with the IDs of the records to be removed"),
):
    dataset = await _get_dataset(db, dataset_id)

    await authorize(current_user, DatasetPolicyV1.delete_records(dataset))

    record_ids = parse_uuids(ids)
    num_records = len(record_ids)

    if num_records == 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No record IDs provided")

    if num_records > DELETE_DATASET_RECORDS_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot delete more than {DELETE_DATASET_RECORDS_LIMIT} records at once",
        )

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
    metadata: MetadataQueryParams = Depends(),
    sort_by_query_param: SortByQueryParamParsed,
    include: Optional[RecordIncludeParam] = Depends(parse_record_include_param),
    response_statuses: List[ResponseStatusFilter] = Query([], alias="response_status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, ge=1, le=LIST_DATASET_RECORDS_LIMIT_LE),
    current_user: User = Security(auth.get_current_user),
):
    dataset = await _get_dataset(db, dataset_id, with_fields=True)

    await authorize(current_user, DatasetPolicyV1.search_records(dataset))

    await _validate_search_records_query(db, body, dataset_id)

    search_responses = await _get_search_responses(
        db=db,
        search_engine=search_engine,
        dataset=dataset,
        search_records_query=body,
        parsed_metadata=metadata.metadata_parsed,
        limit=limit,
        offset=offset,
        user=current_user,
        response_statuses=response_statuses,
        sort_by_query_param=sort_by_query_param,
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
        user_id=current_user.id,
    )

    for record in records:
        record_id_score_map[record.id]["search_record"] = SearchRecord(
            record=RecordSchema.from_orm(record), query_score=record_id_score_map[record.id]["query_score"]
        )

    return SearchRecordsResult(
        items=[record["search_record"] for record in record_id_score_map.values()], total=search_responses.total
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
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    dataset_id: UUID,
    body: SearchRecordsQuery,
    metadata: MetadataQueryParams = Depends(),
    sort_by_query_param: SortByQueryParamParsed,
    include: Optional[RecordIncludeParam] = Depends(parse_record_include_param),
    response_statuses: List[ResponseStatusFilter] = Query([], alias="response_status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, ge=1, le=LIST_DATASET_RECORDS_LIMIT_LE),
    current_user: User = Security(auth.get_current_user),
):
    dataset = await _get_dataset(db, dataset_id, with_fields=True)

    await authorize(current_user, DatasetPolicyV1.search_records_with_all_responses(dataset))

    await _validate_search_records_query(db, body, dataset_id)

    search_responses = await _get_search_responses(
        db=db,
        search_engine=search_engine,
        dataset=dataset,
        search_records_query=body,
        limit=limit,
        offset=offset,
        parsed_metadata=metadata.metadata_parsed,
        response_statuses=response_statuses,
        sort_by_query_param=sort_by_query_param,
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
            record=RecordSchema.from_orm(record), query_score=record_id_score_map[record.id]["query_score"]
        )

    return SearchRecordsResult(
        items=[record["search_record"] for record in record_id_score_map.values()], total=search_responses.total
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
    dataset = await _get_dataset(db, dataset_id)

    await authorize(current_user, DatasetPolicyV1.search_records(dataset))

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
