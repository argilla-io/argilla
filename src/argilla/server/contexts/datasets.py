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

from argilla.server.models import Annotation, Dataset, DatasetStatus, Record, Response
from argilla.server.schemas.v1.datasets import (
    AnnotationCreate,
    DatasetCreate,
    RecordsCreate,
)
from argilla.server.schemas.v1.records import ResponseCreate
from argilla.server.security.model import User
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, contains_eager, joinedload

LIST_RECORDS_LIMIT = 20


def get_dataset_by_id(db: Session, dataset_id: UUID):
    return db.get(Dataset, dataset_id)


def get_dataset_by_name_and_workspace_id(db: Session, name: str, workspace_id: UUID):
    return db.query(Dataset).filter_by(name=name, workspace_id=workspace_id).first()


def list_datasets(db: Session):
    return db.query(Dataset).order_by(Dataset.inserted_at.asc()).all()


def create_dataset(db: Session, dataset_create: DatasetCreate):
    dataset = Dataset(
        name=dataset_create.name,
        guidelines=dataset_create.guidelines,
        workspace_id=dataset_create.workspace_id,
    )

    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return dataset


def publish_dataset(db: Session, dataset: Dataset):
    if dataset.is_ready:
        raise ValueError("Dataset is already published")

    if _count_annotations_by_dataset_id(db, dataset.id) == 0:
        raise ValueError("Dataset cannot be published without annotations")

    dataset.status = DatasetStatus.ready

    db.commit()
    db.refresh(dataset)

    return dataset


def delete_dataset(db: Session, dataset: Dataset):
    db.delete(dataset)
    db.commit()

    return dataset


def get_annotation_by_id(db: Session, annotation_id: UUID):
    return db.get(Annotation, annotation_id)


def get_annotation_by_name_and_dataset_id(db: Session, name: str, dataset_id: UUID):
    return db.query(Annotation).filter_by(name=name, dataset_id=dataset_id).first()


def create_annotation(db: Session, dataset: Dataset, annotation_create: AnnotationCreate):
    if dataset.is_ready:
        raise ValueError("Annotation cannot be created for a published dataset")

    annotation = Annotation(
        name=annotation_create.name,
        title=annotation_create.title,
        required=annotation_create.required,
        settings=annotation_create.settings.dict(),
        dataset_id=dataset.id,
    )

    db.add(annotation)
    db.commit()
    db.refresh(annotation)

    return annotation


def delete_annotation(db: Session, annotation: Annotation):
    if annotation.dataset.is_ready:
        raise ValueError("Annotations cannot be deleted for a published dataset")

    db.delete(annotation)
    db.commit()

    return annotation


def get_record_by_id(db: Session, record_id: UUID):
    return db.get(Record, record_id)


def list_records(db: Session, dataset: Dataset, offset: int = 0, limit: int = LIST_RECORDS_LIMIT):
    return (
        db.query(Record)
        .filter(Record.dataset_id == dataset.id)
        .order_by(Record.inserted_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def create_records(db: Session, dataset: Dataset, user: User, records_create: RecordsCreate):
    if not dataset.is_ready:
        raise ValueError("Records cannot be created for a non published dataset")

    records = []
    for record_create in records_create.items:
        record = Record(
            fields=record_create.fields,
            external_id=record_create.external_id,
            dataset_id=dataset.id,
        )

        if record_create.response:
            record.responses = [Response(values=record_create.response.values, user_id=user.id)]

        records.append(record)

    db.add_all(records)
    db.commit()


def get_response_by_record_id_and_user_id(db: Session, record_id: UUID, user_id: UUID):
    return db.query(Response).filter_by(record_id=record_id, user_id=user_id).first()


def create_response(db: Session, record: Record, user: User, response_create: ResponseCreate):
    response = Response(
        values=response_create.values,
        record_id=record.id,
        user_id=user.id,
    )

    db.add(response)
    db.commit()
    db.refresh(response)

    return response


def _count_annotations_by_dataset_id(db: Session, dataset_id: UUID):
    return db.query(func.count(Annotation.id)).filter_by(dataset_id=dataset_id).scalar()
