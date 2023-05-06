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
import logging
from typing import List, Optional
from uuid import UUID

from argilla.server.elasticsearch import ElasticSearchEngine
from argilla.server.models import (
    Dataset,
    DatasetStatus,
    Field,
    Question,
    Record,
    Response,
    ResponseStatus,
)
from argilla.server.schemas.v1.datasets import (
    DatasetCreate,
    FieldCreate,
    QuestionCreate,
    RecordInclude,
    RecordsCreate,
    ResponseStatusFilter,
)
from argilla.server.schemas.v1.records import ResponseCreate
from argilla.server.schemas.v1.responses import ResponseUpdate
from argilla.server.security.model import User
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, contains_eager

LIST_RECORDS_LIMIT = 20

_LOGGER = logging.getLogger("argilla.server")


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

    if _count_fields_by_dataset_id(db, dataset.id) == 0:
        raise ValueError("Dataset cannot be published without fields")

    if _count_questions_by_dataset_id(db, dataset.id) == 0:
        raise ValueError("Dataset cannot be published without questions")

    dataset.status = DatasetStatus.ready
    db.commit()
    db.refresh(dataset)

    try:
        # TODO: search engine operations won't raise errors for now.
        #  In a next step, this action must be required to fully publish the dataset
        await search_engine.create_index(dataset)
    except Exception as ex:
        _LOGGER.error(f"Search index cannot be created: {ex}")

    return dataset


def delete_dataset(db: Session, dataset: Dataset):
    db.delete(dataset)
    db.commit()

    return dataset


def get_field_by_id(db: Session, field_id: UUID):
    return db.get(Field, field_id)


def get_field_by_name_and_dataset_id(db: Session, name: str, dataset_id: UUID):
    return db.query(Field).filter_by(name=name, dataset_id=dataset_id).first()


def create_field(db: Session, dataset: Dataset, field_create: FieldCreate):
    if dataset.is_ready:
        raise ValueError("Field cannot be created for a published dataset")

    field = Field(
        name=field_create.name,
        title=field_create.title,
        required=field_create.required,
        settings=field_create.settings.dict(),
        dataset_id=dataset.id,
    )

    db.add(field)
    db.commit()
    db.refresh(field)

    return field


def delete_field(db: Session, field: Field):
    if field.dataset.is_ready:
        raise ValueError("Fields cannot be deleted for a published dataset")

    db.delete(field)
    db.commit()

    return field


def get_question_by_id(db: Session, question_id: UUID):
    return db.get(Question, question_id)


def get_question_by_name_and_dataset_id(db: Session, name: str, dataset_id: UUID):
    return db.query(Question).filter_by(name=name, dataset_id=dataset_id).first()


def create_question(db: Session, dataset: Dataset, question_create: QuestionCreate):
    if dataset.is_ready:
        raise ValueError("Question cannot be created for a published dataset")

    question = Question(
        name=question_create.name,
        title=question_create.title,
        description=question_create.description,
        required=question_create.required,
        settings=question_create.settings.dict(),
        dataset_id=dataset.id,
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question


def delete_question(db: Session, question: Question):
    if question.dataset.is_ready:
        raise ValueError("Questions cannot be deleted for a published dataset")

    db.delete(question)
    db.commit()

    return question


def get_record_by_id(db: Session, record_id: UUID):
    return db.get(Record, record_id)


def list_records_by_dataset_id_and_user_id(
    db: Session,
    dataset_id: UUID,
    user_id: UUID,
    include: List[RecordInclude] = [],
    response_status: Optional[ResponseStatusFilter] = None,
    offset: int = 0,
    limit: int = LIST_RECORDS_LIMIT,
):
    query = db.query(Record)

    if response_status == ResponseStatusFilter.missing:
        query = (
            query.outerjoin(
                Response,
                and_(Response.record_id == Record.id, Response.user_id == user_id),
            )
            .options(contains_eager(Record.responses))
            .filter(and_(Record.dataset_id == dataset_id, Response.status == None))
        )

    else:
        if response_status:
            query = query.join(
                Response,
                and_(
                    Response.record_id == Record.id,
                    Response.user_id == user_id,
                    Response.status == ResponseStatus(response_status),
                ),
            ).options(contains_eager(Record.responses))

        elif RecordInclude.responses in include:
            query = query.outerjoin(
                Response,
                and_(Response.record_id == Record.id, Response.user_id == user_id),
            ).options(contains_eager(Record.responses))

        query = query.filter(Record.dataset_id == dataset_id)

    return query.order_by(Record.inserted_at.asc()).offset(offset).limit(limit).all()


def count_records_by_dataset_id(db: Session, dataset_id: UUID):
    return db.query(func.count(Record.id)).filter_by(dataset_id=dataset_id).scalar()


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
            record.responses = [Response(values=jsonable_encoder(record_create.response.values), user_id=user.id)]

        records.append(record)

    db.add_all(records)
    db.commit()


def get_response_by_id(db: Session, response_id: UUID):
    return db.get(Response, response_id)


def get_response_by_record_id_and_user_id(db: Session, record_id: UUID, user_id: UUID):
    return db.query(Response).filter_by(record_id=record_id, user_id=user_id).first()


def list_responses_by_record_id(db: Session, record_id: UUID):
    return db.query(Response).filter_by(record_id=record_id).order_by(Response.inserted_at.asc()).all()


def count_responses_by_dataset_id_and_user_id(db: Session, dataset_id: UUID, user_id: UUID):
    return (
        db.query(func.count(Response.id))
        .join(Record, and_(Record.id == Response.record_id, Record.dataset_id == dataset_id))
        .filter(Response.user_id == user_id)
        .scalar()
    )


def count_submitted_responses_by_dataset_id_and_user_id(db: Session, dataset_id: UUID, user_id: UUID):
    return (
        db.query(func.count(Response.id))
        .join(
            Record,
            and_(
                Record.id == Response.record_id,
                Record.dataset_id == dataset_id,
                Response.status == ResponseStatus.submitted,
            ),
        )
        .filter(Response.user_id == user_id)
        .scalar()
    )


def count_discarded_responses_by_dataset_id_and_user_id(db: Session, dataset_id: UUID, user_id: UUID):
    return (
        db.query(func.count(Response.id))
        .join(
            Record,
            and_(
                Record.id == Response.record_id,
                Record.dataset_id == dataset_id,
                Response.status == ResponseStatus.discarded,
            ),
        )
        .filter(Response.user_id == user_id)
        .scalar()
    )


def count_records_with_missing_responses_by_dataset_id_and_user_id(db: Session, dataset_id: UUID, user_id: UUID):
    return (
        db.query(Record.id)
        .outerjoin(
            Response,
            and_(
                Response.record_id == Record.id,
                Response.user_id == user_id,
            ),
        )
        .with_entities(func.count())
        .filter(and_(Record.dataset_id == dataset_id, Response.status == None))
        .scalar()
    )


def create_response(db: Session, record: Record, user: User, response_create: ResponseCreate):
    response = Response(
        values=jsonable_encoder(response_create.values),
        status=response_create.status,
        record_id=record.id,
        user_id=user.id,
    )

    db.add(response)
    db.commit()
    db.refresh(response)

    return response


def update_response(db: Session, response: Response, response_update: ResponseUpdate):
    response.values = jsonable_encoder(response_update.values)
    response.status = response_update.status

    db.commit()
    db.refresh(response)

    return response


def delete_response(db: Session, response: Response):
    db.delete(response)
    db.commit()

    return response


def _count_fields_by_dataset_id(db: Session, dataset_id: UUID):
    return db.query(func.count(Field.id)).filter_by(dataset_id=dataset_id).scalar()


def _count_questions_by_dataset_id(db: Session, dataset_id: UUID):
    return db.query(func.count(Question.id)).filter_by(dataset_id=dataset_id).scalar()
