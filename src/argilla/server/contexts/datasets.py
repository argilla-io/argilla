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
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Tuple, Union
from uuid import UUID

import sqlalchemy
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from argilla.server.contexts import accounts
from argilla.server.enums import DatasetStatus, RecordInclude, ResponseStatusFilter, UserRole
from argilla.server.models import (
    Dataset,
    Field,
    MetadataProperty,
    Question,
    Record,
    Response,
    ResponseStatus,
    ResponseValue,
    Suggestion,
)
from argilla.server.models.suggestions import SuggestionCreateWithRecordId
from argilla.server.schemas.v1.datasets import (
    DatasetCreate,
    FieldCreate,
    MetadataPropertyCreate,
    QuestionCreate,
    RecordsCreate,
)
from argilla.server.schemas.v1.metadata_properties import MetadataPropertyUpdate
from argilla.server.schemas.v1.records import ResponseCreate
from argilla.server.schemas.v1.responses import ResponseUpdate
from argilla.server.search_engine import SearchEngine
from argilla.server.security.model import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from argilla.server.models import MetadataPropertySettings
    from argilla.server.schemas.v1.datasets import DatasetUpdate, RecordsUpdate
    from argilla.server.schemas.v1.fields import FieldUpdate
    from argilla.server.schemas.v1.questions import QuestionUpdate
    from argilla.server.schemas.v1.records import RecordUpdate
    from argilla.server.schemas.v1.suggestions import SuggestionCreate

LIST_RECORDS_LIMIT = 20

VISIBLE_FOR_ANNOTATORS_ALLOWED_ROLES = [UserRole.admin, UserRole.annotator]
NOT_VISIBLE_FOR_ANNOTATORS_ALLOWED_ROLES = [UserRole.admin]


async def _touch_dataset_last_activity_at(db: "AsyncSession", dataset: Dataset) -> Dataset:
    return await db.execute(
        sqlalchemy.update(Dataset).where(Dataset.id == dataset.id).values(last_activity_at=datetime.utcnow())
    )


async def get_dataset_by_id(
    db: "AsyncSession",
    dataset_id: UUID,
    with_fields: bool = False,
    with_questions: bool = False,
    with_metadata_properties: bool = False,
) -> Dataset:
    query = select(Dataset).filter_by(id=dataset_id)
    options = []
    if with_fields:
        options.append(selectinload(Dataset.fields))
    if with_questions:
        options.append(selectinload(Dataset.questions))
    if with_metadata_properties:
        options.append(selectinload(Dataset.metadata_properties))
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
        allow_extra_metadata=dataset_create.allow_extra_metadata,
        workspace_id=dataset_create.workspace_id,
    )


async def _count_required_fields_by_dataset_id(db: "AsyncSession", dataset_id: UUID) -> int:
    result = await db.execute(select(func.count(Field.id)).filter_by(dataset_id=dataset_id, required=True))
    return result.scalar()


async def _count_required_questions_by_dataset_id(db: "AsyncSession", dataset_id: UUID) -> int:
    result = await db.execute(select(func.count(Question.id)).filter_by(dataset_id=dataset_id, required=True))
    return result.scalar()


def _allowed_roles_for_metadata_property_create(metadata_property_create: MetadataPropertyCreate) -> List[UserRole]:
    if metadata_property_create.visible_for_annotators:
        return VISIBLE_FOR_ANNOTATORS_ALLOWED_ROLES
    else:
        return NOT_VISIBLE_FOR_ANNOTATORS_ALLOWED_ROLES


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


async def get_metadata_property_by_id(db: "AsyncSession", metadata_property_id: UUID) -> Union[MetadataProperty, None]:
    return await MetadataProperty.read(db, id=metadata_property_id)


async def get_metadata_property_by_name_and_dataset_id(
    db: "AsyncSession", name: str, dataset_id: UUID
) -> Union[MetadataProperty, None]:
    result = await db.execute(select(MetadataProperty).filter_by(name=name, dataset_id=dataset_id))
    return result.scalar_one_or_none()


async def delete_metadata_property(db: "AsyncSession", metadata_property: MetadataProperty) -> MetadataProperty:
    return await metadata_property.delete(db)


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


async def create_metadata_property(
    db: "AsyncSession",
    search_engine: "SearchEngine",
    dataset: Dataset,
    metadata_property_create: MetadataPropertyCreate,
) -> MetadataProperty:
    async with db.begin_nested():
        metadata_property = await MetadataProperty.create(
            db,
            name=metadata_property_create.name,
            title=metadata_property_create.title,
            settings=metadata_property_create.settings.dict(),
            allowed_roles=_allowed_roles_for_metadata_property_create(metadata_property_create),
            dataset_id=dataset.id,
            autocommit=False,
        )
        if dataset.is_ready:
            await db.flush([metadata_property])
            await search_engine.configure_metadata_property(dataset, metadata_property)

    await db.commit()

    return metadata_property


async def update_metadata_property(
    db: "AsyncSession",
    metadata_property: MetadataProperty,
    metadata_property_update: MetadataPropertyUpdate,
):
    return await metadata_property.update(
        db,
        title=metadata_property_update.title or metadata_property.title,
        allowed_roles=_allowed_roles_for_metadata_property_create(metadata_property_update),
    )


async def update_question(db: "AsyncSession", question: Question, question_update: "QuestionUpdate") -> Question:
    params = question_update.dict(exclude_unset=True)
    return await question.update(db, **params)


async def delete_question(db: "AsyncSession", question: Question) -> Question:
    if question.dataset.is_ready:
        raise ValueError("Questions cannot be deleted for a published dataset")

    return await question.delete(db)


async def get_record_by_id(
    db: "AsyncSession", record_id: UUID, with_dataset: bool = False, with_suggestions: bool = False
) -> Union[Record, None]:
    query = select(Record).filter_by(id=record_id)
    if with_dataset:
        query = query.options(
            selectinload(Record.dataset).selectinload(Dataset.questions),
            selectinload(Record.dataset).selectinload(Dataset.metadata_properties),
        )
    if with_suggestions:
        query = query.options(selectinload(Record.suggestions))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_records_by_ids(
    db: "AsyncSession",
    dataset_id: UUID,
    records_ids: List[UUID],
    include: Optional[List[RecordInclude]] = None,
    user_id: Optional[UUID] = None,
) -> List[Record]:
    if include is None:
        include = []

    query = select(Record).filter(Record.dataset_id == dataset_id, Record.id.in_(records_ids))

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
    records = result.unique().scalars().all()

    # Preserve the order of the `record_ids` list
    record_order_map = {record.id: record for record in records}
    ordered_records = [record_order_map[record_id] for record_id in records_ids]

    return ordered_records


async def list_records_by_dataset_id(
    db: "AsyncSession",
    dataset_id: UUID,
    user_id: Optional[UUID] = None,
    include: List[RecordInclude] = [],
    response_statuses: List[ResponseStatusFilter] = [],
    offset: int = 0,
    limit: int = LIST_RECORDS_LIMIT,
) -> Tuple[List[Record], int]:
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

    records_query = (
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
        records_query = records_query.filter(or_(*response_status_filter_expressions))

    if RecordInclude.responses in include:
        records_query = records_query.options(contains_eager(Record.responses))

    if RecordInclude.suggestions in include:
        records_query = records_query.options(joinedload(Record.suggestions))

    records_query = records_query.order_by(Record.inserted_at.asc()).offset(offset).limit(limit)
    result_records = await db.execute(records_query)

    count_query = (
        records_query.with_only_columns(func.count(Record.id.distinct())).order_by(None).offset(None).limit(None)
    )
    result_count = await db.execute(count_query)

    return result_records.unique().scalars().all(), result_count.scalar_one()


async def count_records_by_dataset_id(db: "AsyncSession", dataset_id: UUID) -> int:
    result = await db.execute(select(func.count(Record.id)).filter_by(dataset_id=dataset_id))
    return result.scalar()


_EXTRA_METADATA_FLAG = "extra"


async def _validate_metadata(
    db: "AsyncSession",
    dataset: Dataset,
    metadata: Dict[str, Any],
    metadata_properties: Optional[Dict[str, Union[MetadataProperty, str]]] = None,
) -> Dict[str, Union[MetadataProperty, Literal["extra"]]]:
    if metadata_properties is None:
        metadata_properties = {}

    for name, value in metadata.items():
        metadata_property = metadata_properties.get(name)

        if metadata_property is None:
            metadata_property = await get_metadata_property_by_name_and_dataset_id(db, name=name, dataset_id=dataset.id)

            # If metadata property does not exists but extra metadata is allowed, then we set a flag value to
            # avoid querying the database again
            if metadata_property is None and dataset.allow_extra_metadata:
                metadata_property = _EXTRA_METADATA_FLAG
                metadata_properties[name] = metadata_property
            elif metadata_property is not None:
                metadata_properties[name] = metadata_property
            else:
                raise ValueError(
                    f"'{name}' metadata property does not exists for dataset '{dataset.id}' and extra metadata is"
                    " not allowed for this dataset"
                )

        # If metadata property is not found and extra metadata is allowed, then we skip the value validation
        if metadata_property == _EXTRA_METADATA_FLAG:
            continue

        try:
            metadata_property.parsed_settings.check_metadata(value)
        except ValueError as e:
            raise ValueError(f"'{name}' metadata property validation failed because {e}") from e

    return metadata_properties


async def _validate_suggestion(
    db: "AsyncSession",
    suggestion: "SuggestionCreate",
    questions: Optional[Dict[UUID, Question]] = None,
) -> Dict[UUID, Question]:
    if not questions:
        questions = {}

    question = questions.get(suggestion.question_id, None)

    if not question:
        question = await get_question_by_id(db, suggestion.question_id)
        if not question:
            raise ValueError(f"question_id={str(suggestion.question_id)} does not exist")
        questions[suggestion.question_id] = question

    question.parsed_settings.check_response(suggestion)

    return questions


async def create_records(
    db: "AsyncSession", search_engine: SearchEngine, dataset: Dataset, records_create: RecordsCreate
):
    if not dataset.is_ready:
        raise ValueError("Records cannot be created for a non published dataset")

    # Cache dictionaries to avoid querying the database multiple times
    questions: Dict[UUID, Question] = {}
    metadata_properties: Dict[str, Union[MetadataProperty, Literal["extra"]]] = {}

    records = []
    for record_i, record_create in enumerate(records_create.items):
        validate_record_fields(dataset, fields=record_create.fields)

        record = Record(
            fields=record_create.fields,
            metadata_=record_create.metadata,
            external_id=record_create.external_id,
            dataset_id=dataset.id,
        )

        if record_create.responses:
            for response in record_create.responses:
                # TODO(gabrielmbmb): the result of this query should be cached
                if not await accounts.get_user_by_id(db, response.user_id):
                    raise ValueError(f"Provided user_id: {response.user_id!r} is not a valid user id")

                validate_response_values(dataset, values=response.values, status=response.status)

                record.responses.append(
                    Response(
                        values=jsonable_encoder(response.values),
                        status=response.status,
                        user_id=response.user_id,
                    )
                )

        if record_create.suggestions:
            for suggestion in record_create.suggestions:
                try:
                    questions = await _validate_suggestion(db, suggestion, questions=questions)
                except ValueError as e:
                    raise ValueError(f"Provided suggestion for record at position {record_i} is not valid: {e}") from e

                record.suggestions.append(
                    Suggestion(
                        type=suggestion.type,
                        score=suggestion.score,
                        value=suggestion.value,
                        agent=suggestion.agent,
                        question_id=suggestion.question_id,
                    )
                )

        if record_create.metadata:
            try:
                metadata_properties = await _validate_metadata(
                    db,
                    dataset=dataset,
                    metadata=record_create.metadata,
                    metadata_properties=metadata_properties,
                )
            except ValueError as e:
                raise ValueError(f"Provided metadata for record at position {record_i} is not valid: {e}") from e

        records.append(record)

    async with db.begin_nested():
        db.add_all(records)
        await db.flush(records)
        for record in records:
            await record.awaitable_attrs.responses
        await search_engine.index_records(dataset, records)

    await db.commit()


async def _exists_records_with_ids(db: "AsyncSession", dataset_id: UUID, records_ids: List[UUID]) -> List[UUID]:
    result = await db.execute(select(Record.id).filter(Record.dataset_id == dataset_id, Record.id.in_(records_ids)))
    return result.scalars().all()


async def update_records(
    db: "AsyncSession", search_engine: "SearchEngine", dataset: Dataset, records_update: "RecordsUpdate"
) -> None:
    records_ids = [record_update.id for record_update in records_update.items]

    if len(records_ids) != len(set(records_ids)):
        raise ValueError("Found duplicate records IDs")

    existing_records_ids = await _exists_records_with_ids(db, dataset_id=dataset.id, records_ids=records_ids)
    non_existing_records_ids = set(records_ids) - set(existing_records_ids)

    if len(non_existing_records_ids) > 0:
        sorted_non_existing_records_ids = sorted(non_existing_records_ids, key=lambda x: records_ids.index(x))
        records_str = ", ".join([str(record_id) for record_id in sorted_non_existing_records_ids])
        raise ValueError(f"Found records that do not exist: {records_str}")

    # Lists to store the records that will be updated in the database or in the search engine
    records_update_objects: List[Dict[str, Any]] = []
    records_search_engine_update: List[UUID] = []
    records_delete_suggestions: List[UUID] = []

    # Cache dictionaries to avoid querying the database multiple times
    metadata_properties: Dict[str, Union[MetadataProperty, Literal["extra"]]] = {}
    questions: Dict[UUID, Question] = {}

    suggestions = []
    for record_i, record_update in enumerate(records_update.items):
        params = record_update.dict(exclude_unset=True)

        if "metadata_" in params and (metadata := params["metadata_"]) is not None:
            try:
                metadata_properties = await _validate_metadata(db, dataset, metadata, metadata_properties)
            except ValueError as err:
                raise ValueError(f"Provided metadata for record at position {record_i} is not valid: {err}") from err
            records_search_engine_update.append(record_update.id)

        if record_update.suggestions is not None:
            params.pop("suggestions")

            questions_ids = [suggestion.question_id for suggestion in record_update.suggestions]
            if len(questions_ids) != len(set(questions_ids)):
                raise ValueError(f"Found duplicate suggestions question IDs for record at position {record_i}")

            for suggestion_i, suggestion in enumerate(record_update.suggestions):
                try:
                    questions = await _validate_suggestion(db, suggestion, questions)
                    suggestions.append(Suggestion(record_id=record_update.id, **suggestion.dict()))
                except ValueError as err:
                    raise ValueError(
                        f"Provided suggestion for record at position {record_i} and suggestion at position "
                        f"{suggestion_i} is not valid: {err}"
                    ) from err
            records_delete_suggestions.append(record_update.id)

        records_update_objects.append(params)

    async with db.begin_nested():
        params = [Suggestion.record_id.in_(records_delete_suggestions)]
        await Suggestion.delete_many(db, params=params, autocommit=False)
        db.add_all(suggestions)
        await Record.update_many(db, records_update_objects, autocommit=False)
        records = await get_records_by_ids(db, dataset_id=dataset.id, records_ids=records_search_engine_update)
        await search_engine.index_records(dataset, records)

    await db.commit()


async def delete_records(
    db: "AsyncSession", search_engine: "SearchEngine", dataset: Dataset, records_ids: List[UUID]
) -> None:
    async with db.begin_nested():
        params = [Record.id.in_(records_ids), Record.dataset_id == dataset.id]
        records = await Record.delete_many(db=db, params=params, autocommit=False)
        await search_engine.delete_records(dataset=dataset, records=records)

    await db.commit()


async def update_record(
    db: "AsyncSession", search_engine: "SearchEngine", record: Record, record_update: "RecordUpdate"
) -> Record:
    params = record_update.dict(exclude_unset=True)

    if "metadata_" in params and (metadata := params["metadata_"]) is not None:
        await _validate_metadata(db, dataset=record.dataset, metadata=metadata)

    if record_update.suggestions is not None:
        questions_ids = [suggestion.question_id for suggestion in record_update.suggestions]
        if len(questions_ids) != len(set(questions_ids)):
            raise ValueError("Found duplicate suggestions question IDs")

        suggestions = []
        for suggestion in record_update.suggestions:
            try:
                await _validate_suggestion(db, suggestion)
                suggestions.append(Suggestion(**suggestion.dict()))
            except ValueError as err:
                raise ValueError(
                    f"Provided suggestion for question_id={suggestion.question_id} is not valid: {err}"
                ) from err

        # Remove existing suggestions
        record.suggestions = []
        params["suggestions"] = suggestions

    async with db.begin_nested():
        record = await record.update(db, **params, replace_dict=True, autocommit=False)

        # If "metadata" has been included in the update, then we need to also update it in the search engine
        if "metadata_" in params:
            await search_engine.index_records(record.dataset, [record])

    await db.commit()
    return record


async def delete_record(db: "AsyncSession", search_engine: "SearchEngine", record: Record) -> Record:
    async with db.begin_nested():
        record = await record.delete(db=db, autocommit=False)
        await search_engine.delete_records(dataset=record.dataset, records=[record])

    await db.commit()

    return record


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
        await _touch_dataset_last_activity_at(db, record.dataset)
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
        await _touch_dataset_last_activity_at(db, response.record.dataset)
        await search_engine.update_record_response(response)

    await db.commit()

    return response


async def delete_response(db: "AsyncSession", search_engine: SearchEngine, response: Response) -> Response:
    async with db.begin_nested():
        response = await response.delete(db, autocommit=False)
        await _touch_dataset_last_activity_at(db, response.record.dataset)
        await search_engine.delete_record_response(response)

    await db.commit()

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
            question.parsed_settings.check_response(question_response, status)

    if values_copy:
        raise ValueError(f"Error: found responses for non configured questions: {list(values_copy.keys())!r}")


def validate_record_fields(dataset: Dataset, fields: Dict[str, Any]):
    fields_copy = copy.copy(fields or {})
    for field in dataset.fields:
        if field.required and not (field.name in fields_copy and fields_copy.get(field.name) is not None):
            raise ValueError(f"Missing required value for field: {field.name!r}")

        value = fields_copy.pop(field.name, None)
        if value and not isinstance(value, str):
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


async def get_metadata_property_by_id(db: "AsyncSession", metadata_property_id: UUID) -> Optional[MetadataProperty]:
    result = await db.execute(
        select(MetadataProperty).filter_by(id=metadata_property_id).options(selectinload(MetadataProperty.dataset))
    )
    return result.scalar_one_or_none()
