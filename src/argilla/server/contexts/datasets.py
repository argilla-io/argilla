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

from argilla.server.elasticsearch import ElasticSearchEngine
from argilla.server.models import Annotation, Dataset, DatasetStatus
from argilla.server.schemas.v1.datasets import AnnotationCreate, DatasetCreate
from sqlalchemy import func
from sqlalchemy.orm import Session


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


async def publish_dataset(db: Session, search_engine: ElasticSearchEngine, dataset: Dataset):
    if dataset.is_ready:
        raise ValueError("Dataset is already published")

    if _count_annotations_by_dataset_id(db, dataset.id) == 0:
        raise ValueError("Dataset cannot be published without annotations")

    try:
        dataset.status = DatasetStatus.ready
        await search_engine.create_index(dataset)

        db.commit()
        db.refresh(dataset)

        return dataset
    except:
        db.rollback()
        raise


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


def _count_annotations_by_dataset_id(db: Session, dataset_id: UUID):
    return db.query(func.count(Annotation.id)).filter_by(dataset_id=dataset_id).scalar()
