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
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from argilla.server.contexts import accounts, datasets
from argilla.server.database import get_async_db
from argilla.server.enums import MetadataPropertyType, RecordSortField, ResponseStatusFilter, SortOrder
from argilla.server.models import Dataset as DatasetModel
from argilla.server.models import ResponseStatus, User
from argilla.server.policies import DatasetPolicyV1, MetadataPropertyPolicyV1, authorize, is_authorized
from argilla.server.schemas.v1.datasets import (
    Dataset,
    DatasetCreate,
    Datasets,
    DatasetUpdate,
    Field,
    FieldCreate,
    Fields,
    MetadataParsedQueryParam,
    MetadataProperties,
    MetadataProperty,
    MetadataPropertyCreate,
    MetadataQueryParams,
    Metrics,
    Question,
    QuestionCreate,
    Questions,
    RecordIncludeParam,
    Records,
    RecordsCreate,
    RecordsUpdate,
    SearchRecord,
    SearchRecordsQuery,
    SearchRecordsResult,
    VectorQuery,
    VectorSettings,
    VectorSettingsCreate,
    VectorsSettings,
)
from argilla.server.schemas.v1.datasets import Record as RecordSchema
from argilla.server.search_engine import (
    FloatMetadataFilter,
    IntegerMetadataFilter,
    MetadataFilter,
    SearchEngine,
    SortBy,
    TermsMetadataFilter,
    UserResponseStatusFilter,
    get_search_engine,
)
from argilla.server.security import auth
from argilla.server.utils import parse_query_param, parse_uuids
from argilla.utils.telemetry import TelemetryClient, get_telemetry_client

if TYPE_CHECKING:
    from argilla.server.models import Record
    from argilla.server.schemas.v1.datasets import TextQuery
    from argilla.server.search_engine.base import SearchResponses

LIST_DATASET_RECORDS_LIMIT_DEFAULT = 50
LIST_DATASET_RECORDS_LIMIT_LE = 1000
LIST_DATASET_RECORDS_DEFAULT_SORT_BY = {RecordSortField.inserted_at.value: "asc"}
DELETE_DATASET_RECORDS_LIMIT = 100

CREATE_DATASET_VECTOR_SETTINGS_MAX_COUNT = 5

router = APIRouter(tags=["datasets"])

parse_record_include_param = parse_query_param(
    name="include", help="Relationships to include in the response", model=RecordIncludeParam
)


async def _get_dataset(
    db: AsyncSession,
    dataset_id: UUID,
    with_fields: bool = False,
    with_questions: bool = False,
    with_metadata_properties: bool = False,
    with_vectors_settings: bool = False,
) -> DatasetModel:
    dataset = await datasets.get_dataset_by_id(
        db,
        dataset_id,
        with_fields=with_fields,
        with_questions=with_questions,
        with_metadata_properties=with_metadata_properties,
        with_vectors_settings=with_vectors_settings,
    )
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with id `{dataset_id}` not found",
        )
    return dataset


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


_RECORD_SORT_FIELD_VALUES = tuple(field.value for field in RecordSortField)
_VALID_SORT_VALUES = tuple(sort.value for sort in SortOrder)
_METADATA_PROPERTY_SORT_BY_REGEX = re.compile(r"^metadata\.(?P<name>(?=.*[a-z0-9])[a-z0-9_-]+)$")


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


async def _get_search_responses(
    db: "AsyncSession",
    search_engine: "SearchEngine",
    dataset: DatasetModel,
    parsed_metadata: List[MetadataParsedQueryParam],
    limit: int,
    offset: int,
    text_query: Optional["TextQuery"] = None,
    vector_query: Optional["VectorQuery"] = None,
    user: Optional[User] = None,
    response_statuses: Optional[List[ResponseStatusFilter]] = None,
    sort_by_query_param: Optional[Dict[str, str]] = None,
) -> "SearchResponses":
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
        return await search_engine.similarity_search(
            dataset=dataset,
            vector_settings=vector_settings,
            value=vector_query.value,
            record=record,
            query=text_query,
            order=vector_query.order,
            metadata_filters=metadata_filters,
            user_response_status_filter=response_status_filter,
            max_results=limit,
        )
    else:
        return await search_engine.search(
            dataset=dataset,
            query=text_query,
            metadata_filters=metadata_filters,
            user_response_status_filter=response_status_filter,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
        )


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
        parsed_metadata=parsed_metadata,
        limit=limit,
        offset=offset,
        user=user,
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


async def _filter_metadata_properties_by_policy(
    current_user: User, metadata_properties: List[MetadataProperty]
) -> List[MetadataProperty]:
    filtered_metadata_properties = []

    for metadata_property in metadata_properties:
        metadata_property_is_authorized = await is_authorized(
            current_user, MetadataPropertyPolicyV1.get(metadata_property)
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
    await authorize(current_user, DatasetPolicyV1.list(workspace_id))

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
    dataset = await _get_dataset(db, dataset_id, with_fields=True)

    await authorize(current_user, DatasetPolicyV1.get(dataset))

    return Fields(items=dataset.fields)


@router.get("/datasets/{dataset_id}/questions", response_model=Questions)
async def list_dataset_questions(
    *, db: AsyncSession = Depends(get_async_db), dataset_id: UUID, current_user: User = Security(auth.get_current_user)
):
    dataset = await _get_dataset(db, dataset_id, with_questions=True)

    await authorize(current_user, DatasetPolicyV1.get(dataset))

    return Questions(items=dataset.questions)


@router.get("/datasets/{dataset_id}/vectors-settings", response_model=VectorsSettings)
async def list_dataset_vector_settings(
    *, db: AsyncSession = Depends(get_async_db), dataset_id: UUID, current_user: User = Security(auth.get_current_user)
):
    dataset = await _get_dataset(db, dataset_id, with_vectors_settings=True)

    await authorize(current_user, DatasetPolicyV1.get(dataset))

    return VectorsSettings(items=dataset.vectors_settings)


@router.get("/me/datasets/{dataset_id}/metadata-properties", response_model=MetadataProperties)
async def list_current_user_dataset_metadata_properties(
    *, db: AsyncSession = Depends(get_async_db), dataset_id: UUID, current_user: User = Security(auth.get_current_user)
):
    dataset = await _get_dataset(db, dataset_id, with_metadata_properties=True)

    await authorize(current_user, DatasetPolicyV1.get(dataset))

    filtered_metadata_properties = await _filter_metadata_properties_by_policy(
        current_user, dataset.metadata_properties
    )

    return MetadataProperties(items=filtered_metadata_properties)


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


@router.get("/datasets/{dataset_id}", response_model=Dataset)
async def get_dataset(
    *, db: AsyncSession = Depends(get_async_db), dataset_id: UUID, current_user: User = Security(auth.get_current_user)
):
    dataset = await _get_dataset(db, dataset_id)

    await authorize(current_user, DatasetPolicyV1.get(dataset))

    return dataset


@router.get("/me/datasets/{dataset_id}/metrics", response_model=Metrics)
async def get_current_user_dataset_metrics(
    *, db: AsyncSession = Depends(get_async_db), dataset_id: UUID, current_user: User = Security(auth.get_current_user)
):
    dataset = await _get_dataset(db, dataset_id)

    await authorize(current_user, DatasetPolicyV1.get(dataset))

    return {
        "records": {
            "count": await datasets.count_records_by_dataset_id(db, dataset_id),
        },
        "responses": {
            "count": await datasets.count_responses_by_dataset_id_and_user_id(db, dataset_id, current_user.id),
            "submitted": await datasets.count_responses_by_dataset_id_and_user_id(
                db, dataset_id, current_user.id, ResponseStatus(ResponseStatusFilter.submitted)
            ),
            "discarded": await datasets.count_responses_by_dataset_id_and_user_id(
                db, dataset_id, current_user.id, ResponseStatus(ResponseStatusFilter.discarded)
            ),
            "draft": await datasets.count_responses_by_dataset_id_and_user_id(
                db, dataset_id, current_user.id, ResponseStatus(ResponseStatusFilter.draft)
            ),
        },
    }


@router.post("/datasets", status_code=status.HTTP_201_CREATED, response_model=Dataset)
async def create_dataset(
    *,
    db: AsyncSession = Depends(get_async_db),
    dataset_create: DatasetCreate,
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, DatasetPolicyV1.create(dataset_create.workspace_id))

    if not await accounts.get_workspace_by_id(db, dataset_create.workspace_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Workspace with id `{dataset_create.workspace_id}` not found",
        )

    if await datasets.get_dataset_by_name_and_workspace_id(db, dataset_create.name, dataset_create.workspace_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dataset with name `{dataset_create.name}` already exists for workspace with id `{dataset_create.workspace_id}`",
        )

    dataset = await datasets.create_dataset(db, dataset_create)
    return dataset


@router.post("/datasets/{dataset_id}/fields", status_code=status.HTTP_201_CREATED, response_model=Field)
async def create_dataset_field(
    *,
    db: AsyncSession = Depends(get_async_db),
    dataset_id: UUID,
    field_create: FieldCreate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await _get_dataset(db, dataset_id)

    await authorize(current_user, DatasetPolicyV1.create_field(dataset))

    if await datasets.get_field_by_name_and_dataset_id(db, field_create.name, dataset_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Field with name `{field_create.name}` already exists for dataset with id `{dataset_id}`",
        )

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        field = await datasets.create_field(db, dataset, field_create)
        return field
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.post("/datasets/{dataset_id}/questions", status_code=status.HTTP_201_CREATED, response_model=Question)
async def create_dataset_question(
    *,
    db: AsyncSession = Depends(get_async_db),
    dataset_id: UUID,
    question_create: QuestionCreate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await _get_dataset(db, dataset_id)

    await authorize(current_user, DatasetPolicyV1.create_question(dataset))

    if await datasets.get_question_by_name_and_dataset_id(db, question_create.name, dataset_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Question with name `{question_create.name}` already exists for dataset with id `{dataset_id}`",
        )

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        question = await datasets.create_question(db, dataset, question_create)
        return question
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


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
    dataset = await _get_dataset(db, dataset_id)

    await authorize(current_user, DatasetPolicyV1.create_metadata_property(dataset))

    if await datasets.get_metadata_property_by_name_and_dataset_id(db, metadata_property_create.name, dataset_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Metadata property with name `{metadata_property_create.name}` "
            f"already exists for dataset with id `{dataset_id}`",
        )

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        metadata_property = await datasets.create_metadata_property(
            db, search_engine, dataset, metadata_property_create
        )
        return metadata_property
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


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
    dataset = await _get_dataset(db, dataset_id)

    await authorize(current_user, DatasetPolicyV1.create_vector_settings(dataset))

    count_vectors_settings_by_dataset_id = await datasets.count_vectors_settings_by_dataset_id(db, dataset_id)
    if count_vectors_settings_by_dataset_id >= CREATE_DATASET_VECTOR_SETTINGS_MAX_COUNT:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"The maximum number of vector settings has been reached for dataset with id `{dataset_id}`",
        )

    if await datasets.get_vector_settings_by_name_and_dataset_id(db, vector_settings_create.name, dataset_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vector settings with name `{vector_settings_create.name}` already exists for dataset with id"
            f" `{dataset_id}`",
        )

    try:
        vector_settings = await datasets.create_vector_settings(
            db, search_engine, dataset=dataset, vector_settings_create=vector_settings_create
        )
        return vector_settings
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


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

    search_responses = await _get_search_responses(
        db=db,
        search_engine=search_engine,
        dataset=dataset,
        text_query=body.query.text,
        vector_query=body.query.vector,
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

    search_responses = await _get_search_responses(
        db=db,
        search_engine=search_engine,
        dataset=dataset,
        text_query=body.query.text,
        vector_query=body.query.vector,
        parsed_metadata=metadata.metadata_parsed,
        limit=limit,
        offset=offset,
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


@router.put("/datasets/{dataset_id}/publish", response_model=Dataset)
async def publish_dataset(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
) -> DatasetModel:
    dataset = await _get_dataset(
        db, dataset_id, with_fields=True, with_questions=True, with_metadata_properties=True, with_vectors_settings=True
    )

    await authorize(current_user, DatasetPolicyV1.publish(dataset))
    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    #  After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        dataset = await datasets.publish_dataset(db, search_engine, dataset)

        telemetry_client.track_data(
            action="PublishedDataset",
            data={"questions": list(set([question.settings["type"] for question in dataset.questions]))},
        )

        return dataset
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.delete("/datasets/{dataset_id}", response_model=Dataset)
async def delete_dataset(
    *,
    db: AsyncSession = Depends(get_async_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await _get_dataset(db, dataset_id)

    await authorize(current_user, DatasetPolicyV1.delete(dataset))

    await datasets.delete_dataset(db, search_engine, dataset=dataset)

    return dataset


@router.patch("/datasets/{dataset_id}", response_model=Dataset)
async def update_dataset(
    *,
    db: AsyncSession = Depends(get_async_db),
    dataset_id: UUID,
    dataset_update: DatasetUpdate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = await _get_dataset(db, dataset_id)

    await authorize(current_user, DatasetPolicyV1.update(dataset))

    return await datasets.update_dataset(db, dataset=dataset, dataset_update=dataset_update)
