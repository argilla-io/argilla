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

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from argilla.server.contexts import datasets
from argilla.server.database import get_db
from argilla.server.policies import DatasetPolicyV1, authorize
from argilla.server.schemas.v1.datasets import (
    Annotation,
    AnnotationCreate,
    Dataset,
    DatasetCreate,
)
from argilla.server.security import auth
from argilla.server.security.model import User

router = APIRouter(tags=["datasets"])


def _get_dataset(db: Session, dataset_id: UUID):
    dataset = datasets.get_dataset_by_id(db, dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with id `{dataset_id}` not found",
        )

    return dataset


@router.get("/datasets", response_model=List[Dataset])
def list_datasets(
    *,
    db: Session = Depends(get_db),
    current_user: User = Security(auth.get_current_user),
):
    authorize(current_user, DatasetPolicyV1.list)

    if current_user.is_admin:
        return datasets.list_datasets(db)
    else:
        return current_user.datasets


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


@router.get("/datasets/{dataset_id}/annotations", response_model=List[Annotation])
def get_dataset_annotations(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.get(dataset))

    return dataset.annotations


@router.post("/datasets", status_code=status.HTTP_201_CREATED, response_model=Dataset)
def create_dataset(
    *,
    db: Session = Depends(get_db),
    dataset_create: DatasetCreate,
    current_user: User = Security(auth.get_current_user),
):
    authorize(current_user, DatasetPolicyV1.create)

    if datasets.get_dataset_by_name_and_workspace_id(db, dataset_create.name, dataset_create.workspace_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dataset with name `{dataset_create.name}` already exists for workspace with id `{dataset_create.workspace_id}`",
        )

    return datasets.create_dataset(db, dataset_create)


@router.post("/datasets/{dataset_id}/annotations", status_code=status.HTTP_201_CREATED, response_model=Annotation)
def create_dataset_annotation(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    annotation_create: AnnotationCreate,
    current_user: User = Security(auth.get_current_user),
):
    dataset = _get_dataset(db, dataset_id)

    authorize(current_user, DatasetPolicyV1.create_annotation(dataset))

    if datasets.get_annotation_by_name_and_dataset_id(db, annotation_create.name, dataset_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Annotation with name `{annotation_create.name}` already exists for dataset with id `{dataset_id}`",
        )

    return datasets.create_annotation(db, dataset, annotation_create)


@router.put("/datasets/{dataset_id}/publish", response_model=Dataset)
def publish_dataset(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    authorize(current_user, DatasetPolicyV1.publish)

    dataset = _get_dataset(db, dataset_id)

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        return datasets.publish_dataset(db, dataset)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.delete("/datasets/{dataset_id}", response_model=Dataset)
def delete_dataset(
    *,
    db: Session = Depends(get_db),
    dataset_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    authorize(current_user, DatasetPolicyV1.delete)

    dataset = _get_dataset(db, dataset_id)

    datasets.delete_dataset(db, dataset)

    return dataset
