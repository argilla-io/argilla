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

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.orm import Session

from argilla.server.commons.telemetry import TelemetryClient, get_telemetry_client
from argilla.server.contexts import accounts, datasets
from argilla.server.database import get_db
from argilla.server.enums import ResponseStatusFilter
from argilla.server.models import ResponseStatus, User
from argilla.server.policies import DatasetPolicyV1, authorize
from argilla.server.schemas.v1.datasets import (
    Dataset,
    DatasetCreate,
    Datasets,
    Field,
    FieldCreate,
    Fields,
    Metrics,
    Question,
    QuestionCreate,
    Questions,
    Record,
    RecordInclude,
    Records,
    RecordsCreate,
    SearchRecord,
    SearchRecordsQuery,
    SearchRecordsResult,
)
from argilla.server.search_engine import (
    SearchEngine,
    UserResponseStatusFilter,
    get_search_engine,
)
from argilla.server.security import auth

LIST_DATASET_RECORDS_LIMIT_DEFAULT = 50
LIST_DATASET_RECORDS_LIMIT_LTE = 1000

router = APIRouter(tags=["datasets"])


def _get_dataset(db: Session, dataset_id: UUID):
    dataset = datasets.get_dataset_by_id(db, dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with id `{dataset_id}` not found",
        )

    return dataset


@router.get("/me/datasets", response_model=Datasets)
def list_current_user_datasets(
    *,
    db: Session = Depends(get_db),
    current_user: User = Security(auth.get_current_user),
):
    authorize(current_user, DatasetPolicyV1.list)

    if current_user.is_owner:
        return Datasets(items=datasets.list_datasets(db))
    else:
        return Datasets(items=current_user.datasets)


@router.get("/datasets/{dataset_id}/fields", response_model=Fields)
def list_dataset_fields(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.get(dataset))

    return Fields(items=dataset.fields)


@router.get("/datasets/{dataset_id}/questions", response_model=Questions)
def list_dataset_questions(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.get(dataset))

    return Questions(items=dataset.questions)


@router.get("/me/datasets/{dataset_id}/records", response_model=Records, response_model_exclude_unset=True)
def list_current_user_dataset_records(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    include: List[RecordInclude] = Query([]),
    response_status: Optional[ResponseStatusFilter] = Query(None),
    offset: int = 0,
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, lte=LIST_DATASET_RECORDS_LIMIT_LTE),
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.get(dataset))

    records = datasets.list_records_by_dataset_id_and_user_id(
        db, dataset_id, current_user.id, include=include, response_status=response_status, offset=offset, limit=limit
    )

    return Records(items=records)


@router.get("/datasets/{dataset_id}/records", response_model=Records, response_model_exclude_unset=True)
def list_dataset_records(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    include: Optional[List[RecordInclude]] = Query([]),
    offset: int = 0,
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, lte=LIST_DATASET_RECORDS_LIMIT_LTE),
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.list_dataset_records_will_all_responses(dataset))

    records = datasets.list_records_by_dataset_id(db, dataset_id, include=include, offset=offset, limit=limit)

    return Records(items=records)


@router.get("/datasets/{dataset_id}", response_model=Dataset)
def get_dataset(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.get(dataset))

    return dataset


@router.get("/me/datasets/{dataset_id}/metrics", response_model=Metrics)
def get_current_user_dataset_metrics(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.get(dataset))

    return {
        "records": {
            "count": datasets.count_records_by_dataset_id(db, dataset_id),
        },
        "responses": {
            "count": datasets.count_responses_by_dataset_id_and_user_id(db, dataset_id, current_user.id),
            "submitted": datasets.count_responses_by_dataset_id_and_user_id(
                db, dataset_id, current_user.id, ResponseStatus(ResponseStatusFilter.submitted)
            ),
            "discarded": datasets.count_responses_by_dataset_id_and_user_id(
                db, dataset_id, current_user.id, ResponseStatus(ResponseStatusFilter.discarded)
            ),
            "draft": datasets.count_responses_by_dataset_id_and_user_id(
                db, dataset_id, current_user.id, ResponseStatus(ResponseStatusFilter.draft)
            ),
        },
    }


@router.post("/datasets", status_code=status.HTTP_201_CREATED, response_model=Dataset)
def create_dataset(
    *,
    db: Session = Depends(get_db),
    dataset_create: DatasetCreate,
    current_user: User = Security(auth.get_current_user),
):
    authorize(current_user, DatasetPolicyV1.create(dataset_create.workspace_id))

    if not accounts.get_workspace_by_id(db, dataset_create.workspace_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Workspace with id `{dataset_create.workspace_id}` not found",
        )

    if datasets.get_dataset_by_name_and_workspace_id(db, dataset_create.name, dataset_create.workspace_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dataset with name `{dataset_create.name}` already exists for workspace with id `{dataset_create.workspace_id}`",
        )

    return datasets.create_dataset(db, dataset_create)


@router.post("/datasets/{dataset_id}/fields", status_code=status.HTTP_201_CREATED, response_model=Field)
def create_dataset_field(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    field_create: FieldCreate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.create_field(dataset))

    if datasets.get_field_by_name_and_dataset_id(db, field_create.name, dataset_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Field with name `{field_create.name}` already exists for dataset with id `{dataset_id}`",
        )

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        return datasets.create_field(db, dataset, field_create)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.post("/datasets/{dataset_id}/questions", status_code=status.HTTP_201_CREATED, response_model=Question)
def create_dataset_question(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    question_create: QuestionCreate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.create_question(dataset))

    if datasets.get_question_by_name_and_dataset_id(db, question_create.name, dataset_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Question with name `{question_create.name}` already exists for dataset with id `{dataset_id}`",
        )

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        return datasets.create_question(db, dataset, question_create)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.post("/datasets/{dataset_id}/records", status_code=status.HTTP_204_NO_CONTENT)
async def create_dataset_records(
    *,
    db: Session = Depends(get_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    dataset_id: UUID,
    records_create: RecordsCreate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.create_records(dataset))

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    #  After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        await datasets.create_records(db, search_engine, dataset=dataset, records_create=records_create)
        telemetry_client.track_data(action="DatasetRecordsCreated", data={"records": len(records_create.items)})
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.post(
    "/me/datasets/{dataset_id}/records/search",
    status_code=status.HTTP_200_OK,
    response_model=SearchRecordsResult,
    response_model_exclude_unset=True,
)
async def search_dataset_records(
    *,
    db: Session = Depends(get_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    dataset_id: UUID,
    query: SearchRecordsQuery,
    include: List[RecordInclude] = Query([]),
    response_status: Optional[ResponseStatusFilter] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(default=LIST_DATASET_RECORDS_LIMIT_DEFAULT, lte=LIST_DATASET_RECORDS_LIMIT_LTE),
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)
    authorize(current_user, DatasetPolicyV1.search_records(dataset))

    search_engine_query = query.query
    if search_engine_query.text.field and not datasets.get_field_by_name_and_dataset_id(
        db, search_engine_query.text.field, dataset_id
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Field `{search_engine_query.text.field}` not found in dataset `{dataset_id}`.",
        )

    user_response_status_filter = None
    if response_status:
        user_response_status_filter = UserResponseStatusFilter(user=current_user, status=response_status)

    search_responses = await search_engine.search(
        dataset=dataset,
        query=search_engine_query,
        user_response_status_filter=user_response_status_filter,
        offset=offset,
        limit=limit,
    )

    record_id_score_map = {
        response.record_id: {"query_score": response.score, "search_record": None}
        for response in search_responses.items
    }
    records = datasets.get_records_by_ids(
        db=db,
        dataset_id=dataset_id,
        record_ids=list(record_id_score_map.keys()),
        include=include,
        user_id=current_user.id,
    )

    for record in records:
        record_id_score_map[record.id]["search_record"] = SearchRecord(
            record=Record.from_orm(record), query_score=record_id_score_map[record.id]["query_score"]
        )

    return SearchRecordsResult(
        items=[record["search_record"] for record in record_id_score_map.values()], total=search_responses.total
    )


@router.put("/datasets/{dataset_id}/publish", response_model=Dataset)
async def publish_dataset(
    *,
    db: Session = Depends(get_db),
    search_engine: SearchEngine = Depends(get_search_engine),
    telemetry_client: TelemetryClient = Depends(get_telemetry_client),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.publish(dataset))
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
    db: Session = Depends(get_db),
    search_engine=Depends(get_search_engine),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.delete(dataset))

    await datasets.delete_dataset(db, search_engine, dataset=dataset)

    return dataset
