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
import copy
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, contains_eager, joinedload

from argilla.server.contexts import accounts
from argilla.server.enums import ResponseStatusFilter
from argilla.server.models import (
    Dataset,
    DatasetStatus,
    Field,
    Question,
    Record,
    Response,
    ResponseStatus,
    ResponseValue,
)
from argilla.server.schemas.v1.datasets import (
    DatasetCreate,
    FieldCreate,
    QuestionCreate,
    RecordInclude,
    RecordsCreate,
)
from argilla.server.schemas.v1.records import ResponseCreate
from argilla.server.schemas.v1.responses import ResponseUpdate
from argilla.server.search_engine import SearchEngine
from argilla.server.security.model import User

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


async def publish_dataset(db: Session, search_engine: SearchEngine, dataset: Dataset):
    if dataset.is_ready:
        raise ValueError("Dataset is already published")

    if _count_fields_by_dataset_id(db, dataset.id) == 0:
        raise ValueError("Dataset cannot be published without fields")

    if _count_questions_by_dataset_id(db, dataset.id) == 0:
        raise ValueError("Dataset cannot be published without questions")

    dataset.status = DatasetStatus.ready
    db.commit()
    db.expire(dataset)

    try:
        await search_engine.create_index(dataset)
    except:
        # TODO: Improve this action using some rollback mechanism
        dataset.status = DatasetStatus.draft
        db.commit()
        db.expire(dataset)
        raise

    return dataset


async def delete_dataset(db: Session, search_engine: SearchEngine, dataset: Dataset):
    db.delete(dataset)
    await search_engine.delete_index(dataset)

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


def get_records_by_ids(
    db: Session,
    dataset_id: UUID,
    record_ids: List[UUID],
    include: List[RecordInclude] = [],
    user_id: Optional[UUID] = None,
) -> List[Record]:
    query = db.query(Record).filter(Record.dataset_id == dataset_id, Record.id.in_(record_ids))
    if RecordInclude.responses in include:
        if user_id:
            query = query.outerjoin(
                Response, and_(Response.record_id == Record.id, Response.user_id == user_id)
            ).options(contains_eager(Record.responses))
        else:
            query = query.options(joinedload(Record.responses))
    return query.all()


def list_records_by_dataset_id(
    db: Session,
    dataset_id: UUID,
    include: List[RecordInclude] = [],
    offset: int = 0,
    limit: int = LIST_RECORDS_LIMIT,
):
    query = db.query(Record)

    if RecordInclude.responses in include:
        query = query.options(joinedload(Record.responses))

    return (
        query.filter(Record.dataset_id == dataset_id)
        .order_by(Record.inserted_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def list_records_by_dataset_id_and_user_id(
    db: Session,
    dataset_id: UUID,
    user_id: UUID,
    include: List[RecordInclude] = [],
    response_status: Optional[ResponseStatusFilter] = None,
    offset: int = 0,
    limit: int = LIST_RECORDS_LIMIT,
):
    query = db.query(Record).filter(Record.dataset_id == dataset_id)

    if response_status == ResponseStatusFilter.missing:
        query = (
            query.outerjoin(
                Response,
                and_(Response.record_id == Record.id, Response.user_id == user_id),
            )
            .filter(Response.status == None)
            .options(contains_eager(Record.responses))
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

    return query.order_by(Record.inserted_at.asc()).offset(offset).limit(limit).all()


def count_records_by_dataset_id(db: Session, dataset_id: UUID):
    return db.query(func.count(Record.id)).filter_by(dataset_id=dataset_id).scalar()


async def create_records(
    db: Session,
    search_engine: SearchEngine,
    dataset: Dataset,
    records_create: RecordsCreate,
):
    if not dataset.is_ready:
        raise ValueError("Records cannot be created for a non published dataset")

    records = []
    for record_create in records_create.items:
        validate_record_fields(dataset, fields=record_create.fields)

        record = Record(
            fields=record_create.fields,
            metadata_=record_create.metadata,
            external_id=record_create.external_id,
            dataset_id=dataset.id,
        )

        if record_create.responses:
            for response in record_create.responses:
                if not accounts.get_user_by_id(db, response.user_id):
                    raise ValueError(f"Provided user_id: {response.user_id!r} is not a valid user id")

                validate_response_values(dataset, values=response.values, status=response.status)

                record.responses.append(
                    Response(values=jsonable_encoder(response.values), status=response.status, user_id=response.user_id)
                )

        records.append(record)

    try:
        db.add_all(records)

        db.commit()
        db.expire_all()

        await search_engine.add_records(dataset, records)
    except:
        # TODO: Improve this action using some rollback mechanism
        for record in records:
            db.delete(record)
        db.commit()
        raise


def get_response_by_id(db: Session, response_id: UUID):
    return db.get(Response, response_id)


def get_response_by_record_id_and_user_id(db: Session, record_id: UUID, user_id: UUID):
    return db.query(Response).filter_by(record_id=record_id, user_id=user_id).first()


def list_responses_by_record_id(db: Session, record_id: UUID):
    return db.query(Response).filter_by(record_id=record_id).order_by(Response.inserted_at.asc()).all()


def count_responses_by_dataset_id_and_user_id(
    db: Session, dataset_id: UUID, user_id: UUID, response_status: Optional[ResponseStatus] = None
) -> int:
    expressions = [Response.user_id == user_id]
    if response_status:
        expressions.append(Response.status == response_status)

    return (
        db.query(func.count(Response.id))
        .join(Record, and_(Record.id == Response.record_id, Record.dataset_id == dataset_id))
        .filter(*expressions)
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


async def create_response(
    db: Session, search_engine: SearchEngine, record: Record, user: User, response_create: ResponseCreate
):
    validate_response_values(record.dataset, values=response_create.values, status=response_create.status)

    response = Response(
        values=jsonable_encoder(response_create.values),
        status=response_create.status,
        record_id=record.id,
        user_id=user.id,
    )

    db.add(response)
    db.flush([response])
    # TODO: Rollback
    await search_engine.update_record_response(response)

    db.commit()
    db.refresh(response)

    return response


async def update_response(
    db: Session, search_engine: SearchEngine, response: Response, response_update: ResponseUpdate
):
    validate_response_values(response.record.dataset, values=response_update.values, status=response_update.status)

    response.values = jsonable_encoder(response_update.values)
    response.status = response_update.status

    db.flush([response])
    # TODO: Rollback
    await search_engine.update_record_response(response)

    db.commit()
    db.refresh(response)

    return response


async def delete_response(db: Session, search_engine: SearchEngine, response: Response):
    db.delete(response)
    # TODO: Rollback
    await search_engine.delete_record_response(response)

    db.commit()

    return response


def validate_response_values(dataset: Dataset, values: Dict[str, ResponseValue], status: ResponseStatus):
    if not values:
        if status != ResponseStatus.discarded:
            raise ValueError("Missing response values")
        return

    values_copy = copy.copy(values or {})
    for question in dataset.questions:
        if (
            question.required
            and status == ResponseStatus.submitted
            and not (question.name in values and values_copy.get(question.name))
        ):
            raise ValueError(f"Missing required question: {question.name!r}")

        question_response = values_copy.pop(question.name, None)
        if question_response:
            question.parsed_settings.check_response(question_response)

    if values_copy:
        raise ValueError(f"Error: found responses for non configured questions: {list(values_copy.keys())!r}")


def validate_record_fields(dataset: Dataset, fields: Dict[str, Any]):
    fields_copy = copy.copy(fields or {})
    for field in dataset.fields:
        if field.required and not (field.name in fields_copy and fields_copy.get(field.name) is not None):
            raise ValueError(f"Missing required value for field: {field.name!r}")

        value = fields_copy.pop(field.name, None)
        if not isinstance(value, str):
            raise ValueError(
                f"Wrong value found for field {field.name!r}. Expected {str.__name__!r}, found {type(value).__name__!r}"
            )

    if fields_copy:
        raise ValueError(f"Error: found fields values for non configured fields: {list(fields_copy.keys())!r}")


def _count_fields_by_dataset_id(db: Session, dataset_id: UUID):
    return db.query(func.count(Field.id)).filter_by(dataset_id=dataset_id).scalar()


def _count_questions_by_dataset_id(db: Session, dataset_id: UUID):
    return db.query(func.count(Question.id)).filter_by(dataset_id=dataset_id).scalar()
