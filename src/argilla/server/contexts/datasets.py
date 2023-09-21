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
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from argilla.server.contexts import accounts
from argilla.server.enums import RecordInclude, ResponseStatusFilter
from argilla.server.models import (
    Dataset,
    DatasetStatus,
    Field,
    Question,
    Record,
    Response,
    ResponseStatus,
    ResponseValue,
    Suggestion,
    Vector,
    VectorSettings,
)
from argilla.server.models.suggestions import SuggestionCreateWithRecordId
from argilla.server.schemas.v1.datasets import (
    DatasetCreate,
    FieldCreate,
    QuestionCreate,
    RecordsCreate,
    ResponseValueCreate,
    VectorCreate,
    VectorCreateWithRecordIdAndDatasetId,
    VectorsCreate,
)
from argilla.server.schemas.v1.datasets import VectorSettings as VectorSettingsSchema
from argilla.server.schemas.v1.records import ResponseCreate
from argilla.server.schemas.v1.responses import ResponseUpdate, ResponseValueUpdate
from argilla.server.search_engine import SearchEngine
from argilla.server.security.model import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from argilla.server.models.questions import QuestionSettings
    from argilla.server.schemas.v1.datasets import DatasetUpdate, VectorSettingsCreate
    from argilla.server.schemas.v1.fields import FieldUpdate
    from argilla.server.schemas.v1.questions import QuestionUpdate
    from argilla.server.schemas.v1.suggestions import SuggestionCreate

LIST_RECORDS_LIMIT = 20


async def get_dataset_by_id(
    db: "AsyncSession",
    dataset_id: UUID,
    with_fields: bool = False,
    with_questions: bool = False,
    with_vectors_settings: bool = False,
) -> Dataset:
    query = select(Dataset).filter_by(id=dataset_id)
    options = []
    if with_fields:
        options.append(selectinload(Dataset.fields))
    if with_questions:
        options.append(selectinload(Dataset.questions))
    if with_vectors_settings:
        options.append(selectinload(Dataset.vectors_settings))
    if options:
        query = query.options(*options)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_dataset_by_name_and_workspace_id(
    db: "AsyncSession", name: str, workspace_id: UUID
) -> Union[Dataset, None]:
    result = await db.execute(select(Dataset).filter_by(name=name, workspace_id=workspace_id))
    return result.scalar_one_or_none()


async def list_datasets(db: "AsyncSession") -> List[Dataset]:
    result = await db.execute(select(Dataset).order_by(Dataset.inserted_at.asc()))
    return result.scalars().all()


async def list_datasets_by_workspace_id(db: "AsyncSession", workspace_id: UUID) -> List[Dataset]:
    result = await db.execute(
        select(Dataset).where(Dataset.workspace_id == workspace_id).order_by(Dataset.inserted_at.asc())
    )
    return result.scalars().all()


async def create_dataset(db: "AsyncSession", dataset_create: DatasetCreate):
    return await Dataset.create(
        db,
        name=dataset_create.name,
        guidelines=dataset_create.guidelines,
        workspace_id=dataset_create.workspace_id,
    )


async def _count_required_fields_by_dataset_id(db: "AsyncSession", dataset_id: UUID) -> int:
    result = await db.execute(select(func.count(Field.id)).filter_by(dataset_id=dataset_id, required=True))
    return result.scalar()


async def _count_required_questions_by_dataset_id(db: "AsyncSession", dataset_id: UUID) -> int:
    result = await db.execute(select(func.count(Question.id)).filter_by(dataset_id=dataset_id, required=True))
    return result.scalar()


async def publish_dataset(db: "AsyncSession", search_engine: SearchEngine, dataset: Dataset) -> Dataset:
    if dataset.is_ready:
        raise ValueError("Dataset is already published")

    if await _count_required_fields_by_dataset_id(db, dataset.id) == 0:
        raise ValueError("Dataset cannot be published without required fields")

    if await _count_required_questions_by_dataset_id(db, dataset.id) == 0:
        raise ValueError("Dataset cannot be published without required questions")

    async with db.begin_nested():
        dataset = await dataset.update(db, status=DatasetStatus.ready, autocommit=False)
        await search_engine.create_index(dataset)

    await db.commit()

    return dataset


async def delete_dataset(db: "AsyncSession", search_engine: SearchEngine, dataset: Dataset) -> Dataset:
    async with db.begin_nested():
        dataset = await dataset.delete(db, autocommit=False)
        await search_engine.delete_index(dataset)

    await db.commit()

    return dataset


async def update_dataset(db: "AsyncSession", dataset: Dataset, dataset_update: "DatasetUpdate") -> Dataset:
    params = dataset_update.dict(exclude_unset=True)
    return await dataset.update(db, **params)


async def get_field_by_id(db: "AsyncSession", field_id: UUID) -> Union[Field, None]:
    result = await db.execute(select(Field).filter_by(id=field_id).options(selectinload(Field.dataset)))
    return result.scalar_one_or_none()


async def get_field_by_name_and_dataset_id(db: "AsyncSession", name: str, dataset_id: UUID) -> Union[Field, None]:
    result = await db.execute(select(Field).filter_by(name=name, dataset_id=dataset_id))
    return result.scalar_one_or_none()


async def create_field(db: "AsyncSession", dataset: Dataset, field_create: FieldCreate) -> Field:
    if dataset.is_ready:
        raise ValueError("Field cannot be created for a published dataset")

    return await Field.create(
        db,
        name=field_create.name,
        title=field_create.title,
        required=field_create.required,
        settings=field_create.settings.dict(),
        dataset_id=dataset.id,
    )


async def update_field(db: "AsyncSession", field: Field, field_update: "FieldUpdate") -> Field:
    params = field_update.dict(exclude_unset=True)
    return await field.update(db, **params)


async def delete_field(db: "AsyncSession", field: Field) -> Field:
    if field.dataset.is_ready:
        raise ValueError("Fields cannot be deleted for a published dataset")

    return await field.delete(db)


async def get_question_by_id(db: "AsyncSession", question_id: UUID) -> Union[Question, None]:
    result = await db.execute(select(Question).filter_by(id=question_id).options(selectinload(Question.dataset)))
    return result.scalar_one_or_none()


async def get_question_by_name_and_dataset_id(db: "AsyncSession", name: str, dataset_id: UUID) -> Union[Question, None]:
    result = await db.execute(select(Question).filter_by(name=name, dataset_id=dataset_id))
    return result.scalar_one_or_none()


async def create_question(db: "AsyncSession", dataset: Dataset, question_create: QuestionCreate) -> Question:
    if dataset.is_ready:
        raise ValueError("Question cannot be created for a published dataset")

    return await Question.create(
        db,
        name=question_create.name,
        title=question_create.title,
        description=question_create.description,
        required=question_create.required,
        settings=question_create.settings.dict(),
        dataset_id=dataset.id,
    )


async def update_question(db: "AsyncSession", question: Question, question_update: "QuestionUpdate") -> Question:
    params = question_update.dict(exclude_unset=True)
    return await question.update(db, **params)


async def delete_question(db: "AsyncSession", question: Question) -> Question:
    if question.dataset.is_ready:
        raise ValueError("Questions cannot be deleted for a published dataset")

    return await question.delete(db)


async def get_vector_settings_by_id(
    db: "AsyncSession", vector_settings_id: UUID, dataset_id: Optional[UUID] = None
) -> Union[VectorSettings, None]:
    filters = [VectorSettings.id == vector_settings_id]
    if dataset_id:
        filters.append(VectorSettings.dataset_id == dataset_id)
    result = await db.execute(select(VectorSettings).where(*filters).options(selectinload(VectorSettings.dataset)))
    return result.scalar_one_or_none()


async def get_vector_settings_by_name_and_dataset_id(
    db: "AsyncSession", name: str, dataset_id: UUID
) -> Union[VectorSettings, None]:
    return await VectorSettings.read_by(db, name=name, dataset_id=dataset_id)


async def delete_vector_settings(db: "AsyncSession", vector_settings: VectorSettings) -> VectorSettings:
    # TODO: for now the search engine does not allow to delete vector settings
    return await vector_settings.delete(db)


async def create_vector_settings(
    db: "AsyncSession", search_engine: "SearchEngine", dataset: Dataset, vector_settings_create: "VectorSettingsCreate"
) -> VectorSettings:
    async with db.begin_nested():
        vector_settings = await VectorSettings.create(
            db,
            name=vector_settings_create.name,
            dimensions=vector_settings_create.dimensions,
            description=vector_settings_create.description,
            dataset_id=dataset.id,
            autocommit=False,
        )

        if dataset.is_ready:
            await db.flush([vector_settings])
            await search_engine.configure_index_vectors(vector_settings)

    await db.commit()

    return vector_settings


async def get_record_by_id(
    db: "AsyncSession", record_id: UUID, with_dataset: bool = False, with_suggestions: bool = False
) -> Union[Record, None]:
    query = select(Record).filter_by(id=record_id)
    if with_dataset:
        query = query.options(selectinload(Record.dataset).selectinload(Dataset.questions))
    if with_suggestions:
        query = query.options(selectinload(Record.suggestions))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def record_exists(db: "AsyncSession", record_id: UUID, dataset_id: Optional[UUID] = None) -> bool:
    filters = [Record.id == record_id]
    if dataset_id:
        filters.append(Record.dataset_id == dataset_id)
    return await db.scalar(select(exists().where(*filters)))


async def delete_record(db: "AsyncSession", search_engine: "SearchEngine", record: Record) -> Record:
    async with db.begin_nested():
        record = await record.delete(db=db, autocommit=False)
        await search_engine.delete_records(dataset=record.dataset, records=[record])

    await db.commit()

    return record


async def delete_records(
    db: "AsyncSession", search_engine: "SearchEngine", dataset: Dataset, records_ids: List[UUID]
) -> None:
    async with db.begin_nested():
        params = [Record.id.in_(records_ids), Record.dataset_id == dataset.id]
        records = await Record.delete_many(db=db, params=params, autocommit=False)
        await search_engine.delete_records(dataset=dataset, records=records)

    await db.commit()


async def get_records_by_ids(
    db: "AsyncSession",
    dataset_id: UUID,
    record_ids: List[UUID],
    include: List[RecordInclude] = [],
    user_id: Optional[UUID] = None,
) -> List[Record]:
    query = select(Record).filter(Record.dataset_id == dataset_id, Record.id.in_(record_ids))
    if RecordInclude.responses in include:
        if user_id:
            query = query.outerjoin(
                Response, and_(Response.record_id == Record.id, Response.user_id == user_id)
            ).options(contains_eager(Record.responses))
        else:
            query = query.options(joinedload(Record.responses))
    if RecordInclude.suggestions in include:
        query = query.options(joinedload(Record.suggestions))
    result = await db.execute(query)
    return result.unique().scalars().all()


async def list_records_by_dataset_id(
    db: "AsyncSession",
    dataset_id: UUID,
    user_id: Optional[UUID] = None,
    include: List[RecordInclude] = [],
    response_statuses: List[ResponseStatusFilter] = [],
    offset: int = 0,
    limit: int = LIST_RECORDS_LIMIT,
) -> List[Record]:
    response_statuses_ = [
        ResponseStatus(response_status)
        for response_status in response_statuses
        if response_status != ResponseStatusFilter.missing
    ]

    response_status_filter_expressions = []

    if response_statuses_:
        response_status_filter_expressions.append(Response.status.in_(response_statuses_))

    if ResponseStatusFilter.missing in response_statuses:
        response_status_filter_expressions.append(Response.status.is_(None))

    query = (
        select(Record)
        .filter(Record.dataset_id == dataset_id)
        .outerjoin(
            Response,
            Response.record_id == Record.id
            if user_id is None
            else and_(Response.record_id == Record.id, Response.user_id == user_id),
        )
    )

    if response_status_filter_expressions:
        query = query.filter(or_(*response_status_filter_expressions))

    if RecordInclude.responses in include:
        query = query.options(contains_eager(Record.responses))

    if RecordInclude.suggestions in include:
        query = query.options(joinedload(Record.suggestions))

    if RecordInclude.vectors in include:
        query = query.options(joinedload(Record.vectors))

    query = query.order_by(Record.inserted_at.asc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.unique().scalars().all()


async def count_records_by_dataset_id(db: "AsyncSession", dataset_id: UUID) -> int:
    result = await db.execute(select(func.count(Record.id)).filter_by(dataset_id=dataset_id))
    return result.scalar()


async def validate_user(db: "AsyncSession", user_id: UUID, users_ids: Optional[Set[UUID]]) -> Set[UUID]:
    if not users_ids:
        users_ids = set()

    if user_id not in users_ids:
        if not await accounts.user_exists(db, user_id):
            raise ValueError(f"user_id={str(user_id)} does not exist")
        users_ids.add(user_id)

    return users_ids


async def validate_suggestion(
    db: "AsyncSession",
    suggestion: "SuggestionCreate",
    questions_settings: Optional[Dict[UUID, "QuestionSettings"]] = None,
) -> Dict[UUID, "QuestionSettings"]:
    if not questions_settings:
        questions_settings = {}

    question_settings = questions_settings.get(suggestion.question_id, None)

    if not question_settings:
        question = await get_question_by_id(db, suggestion.question_id)
        if not question:
            raise ValueError(f"question_id={str(suggestion.question_id)} does not exist")
        question_settings = question.parsed_settings
        questions_settings[suggestion.question_id] = question_settings

    question_settings.check_response(suggestion)

    return questions_settings


async def validate_vector(
    db: "AsyncSession",
    dataset_id: UUID,
    vector: VectorCreate,
    vectors_settings: Optional[Dict[UUID, VectorSettingsSchema]] = None,
) -> Dict[UUID, VectorSettingsSchema]:
    if vectors_settings is None:
        vectors_settings = {}

    vector_settings = vectors_settings.get(vector.vector_settings_id, None)

    if not vector_settings:
        vector_settings = await get_vector_settings_by_id(db, vector.vector_settings_id, dataset_id)
        if not vector_settings:
            raise ValueError(
                f"vector_settings_id={str(vector.vector_settings_id)} does not exist for dataset_id={str(dataset_id)}"
            )
        vector_settings = VectorSettingsSchema.from_orm(vector_settings)
        vectors_settings[vector.vector_settings_id] = vector_settings

    vector_settings.check_vector(vector)

    return vectors_settings


async def create_records(
    db: "AsyncSession", search_engine: SearchEngine, dataset: Dataset, records_create: RecordsCreate
):
    if not dataset.is_ready:
        raise ValueError("Records cannot be created for a non published dataset")

    records = []
    vectors = []
    for record_i, record_create in enumerate(records_create.items):
        validate_record_fields(dataset, fields=record_create.fields)

        record = Record(
            fields=record_create.fields,
            metadata_=record_create.metadata,
            external_id=record_create.external_id,
            dataset_id=dataset.id,
        )

        if record_create.responses:
            users_ids: Set[UUID] = set()
            for i, response in enumerate(record_create.responses):
                try:
                    users_ids = await validate_user(db, response.user_id, users_ids)
                    validate_response_values(dataset, values=response.values, status=response.status)
                except ValueError as e:
                    raise ValueError(
                        f"Provided response at position {i} of record at position {record_i} is not valid: {e}"
                    ) from e

                record.responses.append(
                    Response(
                        values=jsonable_encoder(response.values),
                        status=response.status,
                        user_id=response.user_id,
                    )
                )

        if record_create.suggestions:
            questions_settings: Dict[UUID, "QuestionSettings"] = {}
            for i, suggestion in enumerate(record_create.suggestions):
                try:
                    questions_settings = await validate_suggestion(db, suggestion, questions_settings)
                except ValueError as e:
                    raise ValueError(
                        f"Provided suggestion at position {i} for record at position {record_i} is not valid: {e}"
                    ) from e

                record.suggestions.append(
                    Suggestion(
                        type=suggestion.type,
                        score=suggestion.score,
                        value=suggestion.value,
                        agent=suggestion.agent,
                        question_id=suggestion.question_id,
                    )
                )

        if record_create.vectors:
            vectors_settings: Dict[UUID, VectorSettingsSchema] = {}
            for i, vector in enumerate(record_create.vectors):
                try:
                    vectors_settings = await validate_vector(db, dataset.id, vector, vectors_settings)
                except ValueError as e:
                    raise ValueError(
                        f"Provided vector at position {i} of record at position {record_i} is not valid: {e}"
                    ) from e

                vector = Vector(value=vector.value, dataset_id=dataset.id, vector_settings_id=vector.vector_settings_id)

                record.vectors.append(vector)
                vectors.append(vector)

        records.append(record)

    async with db.begin_nested():
        db.add_all(records)
        await db.flush(records)
        for record in records:
            await record.awaitable_attrs.responses
        await search_engine.add_records(dataset, records)
        if vectors:
            await search_engine.set_records_vectors(dataset, vectors)

    await db.commit()


async def get_response_by_id(db: "AsyncSession", response_id: UUID) -> Union[Response, None]:
    result = await db.execute(
        select(Response)
        .filter_by(id=response_id)
        .options(selectinload(Response.record).selectinload(Record.dataset).selectinload(Dataset.questions))
    )
    return result.scalar_one_or_none()


async def get_response_by_record_id_and_user_id(
    db: "AsyncSession", record_id: UUID, user_id: UUID
) -> Union[Response, None]:
    result = await db.execute(select(Response).filter_by(record_id=record_id, user_id=user_id))
    return result.scalar_one_or_none()


async def count_responses_by_dataset_id_and_user_id(
    db: "AsyncSession", dataset_id: UUID, user_id: UUID, response_status: Optional[ResponseStatus] = None
) -> int:
    expressions = [Response.user_id == user_id]
    if response_status:
        expressions.append(Response.status == response_status)

    result = await db.execute(
        select(func.count(Response.id))
        .join(Record, and_(Record.id == Response.record_id, Record.dataset_id == dataset_id))
        .filter(*expressions)
    )
    return result.scalar()


async def create_response(
    db: "AsyncSession", search_engine: SearchEngine, record: Record, user: User, response_create: ResponseCreate
) -> Response:
    validate_response_values(record.dataset, values=response_create.values, status=response_create.status)

    async with db.begin_nested():
        response = await Response.create(
            db,
            values=jsonable_encoder(response_create.values),
            status=response_create.status,
            record_id=record.id,
            user_id=user.id,
            autocommit=False,
        )
        await db.flush([response])
        await search_engine.update_record_response(response)

    await db.commit()

    return response


async def update_response(
    db: "AsyncSession", search_engine: SearchEngine, response: Response, response_update: ResponseUpdate
):
    validate_response_values(response.record.dataset, values=response_update.values, status=response_update.status)

    async with db.begin_nested():
        response = await response.update(
            db,
            values=jsonable_encoder(response_update.values),
            status=response_update.status,
            replace_dict=True,
            autocommit=False,
        )
        await search_engine.update_record_response(response)

    await db.commit()

    return response


async def delete_response(db: "AsyncSession", search_engine: SearchEngine, response: Response) -> Response:
    async with db.begin_nested():
        response = await response.delete(db, autocommit=False)
        await search_engine.delete_record_response(response)

    await db.commit()

    return response


def validate_response_values(
    dataset: Dataset,
    values: Union[Dict[str, ResponseValueCreate], Dict[str, ResponseValueUpdate], None],
    status: ResponseStatus,
):
    if not values:
        if status != ResponseStatus.discarded:
            raise ValueError("missing response values")
        return

    values_copy = copy.copy(values or {})
    for question in dataset.questions:
        if (
            question.required
            and status == ResponseStatus.submitted
            and not (question.name in values and values_copy.get(question.name))
        ):
            raise ValueError(f"missing question with name={question.name}")

        question_response = values_copy.pop(question.name, None)
        if question_response:
            question.parsed_settings.check_response(question_response, status)

    if values_copy:
        raise ValueError(f"found responses for non configured questions: {list(values_copy.keys())!r}")


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


async def get_suggestion_by_record_id_and_question_id(
    db: "AsyncSession", record_id: UUID, question_id: UUID
) -> Union[Suggestion, None]:
    result = await db.execute(select(Suggestion).filter_by(record_id=record_id, question_id=question_id))
    return result.scalar_one_or_none()


async def upsert_suggestion(
    db: "AsyncSession", record: Record, question: Question, suggestion_create: "SuggestionCreate"
) -> Suggestion:
    question.parsed_settings.check_response(suggestion_create)
    return await Suggestion.upsert(
        db,
        schema=SuggestionCreateWithRecordId(record_id=record.id, **suggestion_create.dict()),
        constraints=[Suggestion.record_id, Suggestion.question_id],
    )


async def delete_suggestions(db: "AsyncSession", record: Record, suggestions_ids: List[UUID]) -> None:
    params = [Suggestion.id.in_(suggestions_ids), Suggestion.record_id == record.id]
    await Suggestion.delete_many(db=db, params=params)


async def get_suggestion_by_id(db: "AsyncSession", suggestion_id: "UUID") -> Union[Suggestion, None]:
    result = await db.execute(
        select(Suggestion)
        .filter_by(id=suggestion_id)
        .options(selectinload(Suggestion.record).selectinload(Record.dataset))
    )
    return result.scalar_one_or_none()


async def delete_suggestion(db: "AsyncSession", suggestion: Suggestion) -> Suggestion:
    return await suggestion.delete(db)


async def upsert_vectors(
    db: "AsyncSession", search_engine: "SearchEngine", dataset: Dataset, vectors_create: VectorsCreate
) -> List[Vector]:
    vectors_settings: Dict[UUID, VectorSettingsSchema] = {}
    records_ids: Set[UUID] = set()
    for i, vector in enumerate(vectors_create.items):
        # Check provided record exists
        if vector.record_id not in records_ids:
            if not await record_exists(db, record_id=vector.record_id, dataset_id=dataset.id):
                raise ValueError(
                    f"Provided record_id={str(vector.record_id)} at position {i} does not exist for "
                    f"dataset_id={str(dataset.id)}"
                )
            records_ids.add(vector.record_id)

        # Check provided vector settings exists and that the value is valid for the settings
        try:
            vectors_settings = await validate_vector(db, dataset.id, vector, vectors_settings)
        except ValueError as e:
            raise ValueError(f"Provided vector at position {i} is not valid: {e}") from e

    async with db.begin_nested():
        vectors = await Vector.upsert_many(
            db,
            objects=[
                VectorCreateWithRecordIdAndDatasetId(dataset_id=dataset.id, **vector.dict())
                for vector in vectors_create.items
            ],
            constraints=[Vector.record_id, Vector.vector_settings_id],
            autocommit=False,
        )

        await search_engine.set_records_vectors(dataset, vectors)

    await db.commit()

    return vectors
