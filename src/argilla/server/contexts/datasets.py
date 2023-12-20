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
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
)
from uuid import UUID

import sqlalchemy
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import contains_eager, joinedload, selectinload

import argilla.server.errors.future as errors
from argilla.server.contexts import accounts
from argilla.server.enums import DatasetStatus, RecordInclude, UserRole
from argilla.server.models import (
    Dataset,
    Field,
    MetadataProperty,
    Question,
    Record,
    Response,
    ResponseStatus,
    Suggestion,
    Vector,
    VectorSettings,
)
from argilla.server.models.suggestions import SuggestionCreateWithRecordId
from argilla.server.schemas.v1.datasets import (
    DatasetCreate,
    FieldCreate,
    MetadataPropertyCreate,
    QuestionCreate,
    RecordCreate,
    RecordIncludeParam,
    RecordsCreate,
    RecordUpdateWithId,
    ResponseValueCreate,
)
from argilla.server.schemas.v1.datasets import (
    VectorSettings as VectorSettingsSchema,
)
from argilla.server.schemas.v1.metadata_properties import MetadataPropertyUpdate
from argilla.server.schemas.v1.records import ResponseCreate
from argilla.server.schemas.v1.responses import ResponseUpdate, ResponseUpsert, ResponseValueUpdate
from argilla.server.schemas.v1.vectors import Vector as VectorSchema
from argilla.server.search_engine import SearchEngine
from argilla.server.security.model import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from argilla.server.schemas.v1.datasets import (
        DatasetUpdate,
        RecordsUpdate,
        VectorSettingsCreate,
    )
    from argilla.server.schemas.v1.fields import FieldUpdate
    from argilla.server.schemas.v1.questions import QuestionUpdate
    from argilla.server.schemas.v1.records import RecordUpdate
    from argilla.server.schemas.v1.suggestions import SuggestionCreate
    from argilla.server.schemas.v1.vector_settings import VectorSettingsUpdate

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
    with_vectors_settings: bool = False,
) -> Dataset:
    query = select(Dataset).filter_by(id=dataset_id)
    options = []
    if with_fields:
        options.append(selectinload(Dataset.fields))
    if with_questions:
        options.append(selectinload(Dataset.questions))
    if with_metadata_properties:
        options.append(selectinload(Dataset.metadata_properties))
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


async def get_question_by_name_and_dataset_id_or_raise(db: "AsyncSession", name: str, dataset_id: UUID) -> Question:
    question = await get_question_by_name_and_dataset_id(db, name, dataset_id)
    if question is None:
        raise errors.NotFoundError(f"Question with name `{name}` not found for dataset with id `{dataset_id}`")

    return question


async def get_metadata_property_by_name_and_dataset_id(
    db: "AsyncSession", name: str, dataset_id: UUID
) -> Union[MetadataProperty, None]:
    result = await db.execute(select(MetadataProperty).filter_by(name=name, dataset_id=dataset_id))

    return result.scalar_one_or_none()


async def get_metadata_property_by_name_and_dataset_id_or_raise(
    db: "AsyncSession", name: str, dataset_id: UUID
) -> MetadataProperty:
    metadata_property = await get_metadata_property_by_name_and_dataset_id(db, name, dataset_id)
    if metadata_property is None:
        raise errors.NotFoundError(f"Metadata property with name `{name}` not found for dataset with id `{dataset_id}`")

    return metadata_property


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


async def count_vectors_settings_by_dataset_id(db: "AsyncSession", dataset_id: UUID) -> int:
    result = await db.execute(select(func.count(VectorSettings.id)).filter_by(dataset_id=dataset_id))

    return result.scalar()


async def get_vector_settings_by_id(db: "AsyncSession", vector_settings_id: UUID) -> Union[VectorSettings, None]:
    result = await db.execute(
        select(VectorSettings).filter_by(id=vector_settings_id).options(selectinload(VectorSettings.dataset))
    )
    return result.scalar_one_or_none()


async def get_vector_settings_by_name_and_dataset_id(
    db: "AsyncSession", name: str, dataset_id: UUID
) -> Union[VectorSettings, None]:
    return await VectorSettings.read_by(db, name=name, dataset_id=dataset_id)


async def update_vector_settings(
    db: "AsyncSession", vector_settings: VectorSettings, vector_settings_update: "VectorSettingsUpdate"
) -> VectorSettings:
    params = vector_settings_update.dict(exclude_unset=True)
    return await vector_settings.update(db, **params)


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
            title=vector_settings_create.title,
            dimensions=vector_settings_create.dimensions,
            dataset_id=dataset.id,
            autocommit=False,
        )

        if dataset.is_ready:
            await db.flush([vector_settings])
            await search_engine.configure_index_vectors(vector_settings)

    await db.commit()

    return vector_settings


async def get_record_by_id(
    db: "AsyncSession",
    record_id: UUID,
    with_dataset: bool = False,
    with_suggestions: bool = False,
    with_vectors: bool = False,
) -> Union[Record, None]:
    query = select(Record).filter_by(id=record_id)
    if with_dataset:
        query = query.options(
            selectinload(Record.dataset).selectinload(Dataset.questions),
            selectinload(Record.dataset).selectinload(Dataset.metadata_properties),
        )

    if with_suggestions:
        query = query.options(selectinload(Record.suggestions))
    if with_vectors:
        query = query.options(selectinload(Record.vectors))
    result = await db.execute(query)

    return result.scalar_one_or_none()


async def get_records_by_ids(
    db: "AsyncSession",
    dataset_id: UUID,
    records_ids: Iterable[UUID],
    include: Optional["RecordIncludeParam"] = None,
    user_id: Optional[UUID] = None,
) -> List[Record]:
    query = select(Record).filter(Record.dataset_id == dataset_id, Record.id.in_(records_ids))

    if include and include.with_responses:
        if not user_id:
            query = query.options(joinedload(Record.responses))
        else:
            query = query.outerjoin(
                Response, and_(Response.record_id == Record.id, Response.user_id == user_id)
            ).options(contains_eager(Record.responses))

    query = await _configure_query_relationships(query=query, dataset_id=dataset_id, include_params=include)

    result = await db.execute(query)
    records = result.unique().scalars().all()

    # Preserve the order of the `record_ids` list
    record_order_map = {record.id: record for record in records}
    ordered_records = [record_order_map[record_id] for record_id in records_ids]

    return ordered_records


async def _configure_query_relationships(
    query: "Select", dataset_id: UUID, include_params: Optional["RecordIncludeParam"] = None
) -> "Select":
    if not include_params:
        return query

    if include_params.with_suggestions:
        query = query.options(joinedload(Record.suggestions))

    if include_params.with_all_vectors:
        query = query.options(joinedload(Record.vectors).joinedload(Vector.vector_settings))

    elif include_params.with_some_vector:
        vector_settings_ids_subquery = select(VectorSettings.id).filter(
            and_(VectorSettings.dataset_id == dataset_id, VectorSettings.name.in_(include_params.vectors))
        )
        query = query.outerjoin(
            Vector, and_(Vector.record_id == Record.id, Vector.vector_settings_id.in_(vector_settings_ids_subquery))
        ).options(contains_eager(Record.vectors).joinedload(Vector.vector_settings))

    return query


async def count_records_by_dataset_id(db: "AsyncSession", dataset_id: UUID) -> int:
    result = await db.execute(select(func.count(Record.id)).filter_by(dataset_id=dataset_id))
    return result.scalar()


_EXTRA_METADATA_FLAG = "extra"


async def _validate_metadata(
    db: "AsyncSession",
    dataset: Dataset,
    metadata: Dict[str, Any],
    metadata_properties: Optional[Dict[str, Union[MetadataProperty, Literal["extra"]]]] = None,
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


async def validate_user(db: "AsyncSession", user_id: UUID, users_ids: Optional[Set[UUID]]) -> Set[UUID]:
    if not users_ids:
        users_ids = set()

    if user_id not in users_ids:
        if not await accounts.user_exists(db, user_id):
            raise ValueError(f"user_id={str(user_id)} does not exist")
        users_ids.add(user_id)

    return users_ids


async def _validate_vector(
    db: "AsyncSession",
    dataset_id: UUID,
    vector_name: str,
    vector_value: List[float],
    vectors_settings: Optional[Dict[str, VectorSettingsSchema]] = None,
) -> Dict[str, VectorSettingsSchema]:
    if vectors_settings is None:
        vectors_settings = {}

    vector_settings = vectors_settings.get(vector_name, None)
    if not vector_settings:
        vector_settings = await get_vector_settings_by_name_and_dataset_id(db, vector_name, dataset_id)
        if not vector_settings:
            raise ValueError(f"vector with name={str(vector_name)} does not exist for dataset_id={str(dataset_id)}")

        vector_settings = VectorSettingsSchema.from_orm(vector_settings)
        vectors_settings[vector_name] = vector_settings

    vector_settings.check_vector(vector_value)

    return vectors_settings


async def _create_record(
    db: "AsyncSession", dataset: Dataset, record_create: RecordCreate, caches: Dict[str, Any]
) -> Record:
    _validate_record_fields(dataset, fields=record_create.fields)
    caches["metadata_properties_cache"] = await _validate_record_metadata(
        db, dataset, record_create.metadata, caches["metadata_properties_cache"]
    )
    record_responses, caches["users_ids_cache"] = await _build_record_responses(
        db, dataset, record_create, caches["users_ids_cache"]
    )
    record_suggestions, caches["questions_cache"] = await _build_record_suggestions(
        db, record_create, caches["questions_cache"]
    )
    record_vectors, caches["vectors_settings_cache"] = await _build_record_vectors(
        db,
        dataset,
        record_create,
        build_vector_func=lambda value, vector_settings_id: Vector(value=value, vector_settings_id=vector_settings_id),
        cache=caches["vectors_settings_cache"],
    )
    record = Record(
        fields=record_create.fields,
        metadata_=record_create.metadata,
        external_id=record_create.external_id,
        dataset_id=dataset.id,
        responses=record_responses,
        suggestions=record_suggestions,
        vectors=record_vectors,
    )
    return record


async def create_records(
    db: "AsyncSession", search_engine: SearchEngine, dataset: Dataset, records_create: RecordsCreate
):
    if not dataset.is_ready:
        raise ValueError("Records cannot be created for a non published dataset")

    records = []

    caches = {
        "users_ids_cache": set(),
        "questions_cache": {},
        "metadata_properties_cache": {},
        "vectors_settings_cache": {},
    }

    for record_i, record_create in enumerate(records_create.items):
        try:
            record = await _create_record(db, dataset, record_create, caches)
        except ValueError as e:
            raise ValueError(f"Record at position {record_i} is not valid because {e}") from e
        records.append(record)

    async with db.begin_nested():
        db.add_all(records)
        await db.flush(records)
        await _preload_records_relationships_before_index(db, records)
        await search_engine.index_records(dataset, records)

    await db.commit()


async def _load_users_from_responses(responses: Union[Response, Iterable[Response]]) -> None:
    if isinstance(responses, Response):
        responses = [responses]

    # TODO: We should do a single query retrieving all the users from all responses instead of using awaitable_attrs,
    # something similar to what we are already doing in _preload_suggestion_relationships_before_index.
    for response in responses:
        await response.awaitable_attrs.user


async def _load_users_from_record_responses(records: Iterable[Record]) -> None:
    for record in records:
        await _load_users_from_responses(record.responses)


async def _validate_record_metadata(
    db: "AsyncSession",
    dataset: Dataset,
    metadata: Optional[Dict[str, Any]] = None,
    cache: Dict[str, Union[MetadataProperty, Literal["extra"]]] = {},
) -> Dict[str, Union[MetadataProperty, Literal["extra"]]]:
    """Validate metadata for a record."""
    if not metadata:
        return cache

    try:
        cache = await _validate_metadata(db, dataset=dataset, metadata=metadata, metadata_properties=cache)
        return cache
    except ValueError as e:
        raise ValueError(f"metadata is not valid: {e}") from e


async def _build_record_responses(
    db: "AsyncSession",
    dataset: Dataset,
    record_create: RecordCreate,
    cache: Set[UUID] = set(),
) -> Tuple[List[Response], Set[UUID]]:
    """Create responses for a record."""
    if not record_create.responses:
        return [], cache

    responses = []

    for idx, response in enumerate(record_create.responses):
        try:
            cache = await validate_user(db, response.user_id, cache)
            _validate_response_values(dataset, values=response.values, status=response.status)
            responses.append(
                Response(
                    values=jsonable_encoder(response.values),
                    status=response.status,
                    user_id=response.user_id,
                )
            )
        except ValueError as e:
            raise ValueError(f"response at position {idx} is not valid: {e}") from e

    return responses, cache


async def _build_record_suggestions(
    db: "AsyncSession",
    record_schema: Union["RecordCreate", "RecordUpdate", "RecordUpdateWithId"],
    cache: Dict[UUID, Question] = {},
) -> Tuple[List[Suggestion], Dict[UUID, Question]]:
    """Create suggestions for a record."""

    if not record_schema.suggestions:
        return [], cache

    suggestions = []
    for suggestion in record_schema.suggestions:
        try:
            cache = await _validate_suggestion(db, suggestion, questions=cache)
            suggestion = Suggestion(
                type=suggestion.type,
                score=suggestion.score,
                value=suggestion.value,
                agent=suggestion.agent,
                question_id=suggestion.question_id,
            )
            if isinstance(record_schema, RecordUpdateWithId):
                suggestion.record_id = record_schema.id
            suggestions.append(suggestion)
        except ValueError as e:
            raise ValueError(f"suggestion for question_id={suggestion.question_id} is not valid: {e}") from e
    return suggestions, cache


VectorClass = TypeVar("VectorClass")


async def _build_record_vectors(
    db: "AsyncSession",
    dataset: Dataset,
    record_schema: Union["RecordCreate", "RecordUpdate", "RecordUpdateWithId"],
    build_vector_func: Callable[[List[float], UUID], VectorClass],
    cache: Dict[str, VectorSettingsSchema] = {},
) -> Tuple[List[VectorClass], Dict[str, VectorSettingsSchema]]:
    """Create vectors for a record."""
    if not record_schema.vectors:
        return [], cache

    vectors = []
    for vector_name, vector_value in record_schema.vectors.items():
        try:
            cache = await _validate_vector(db, dataset.id, vector_name, vector_value, vectors_settings=cache)
            vectors.append(build_vector_func(vector_value, cache[vector_name].id))
        except ValueError as e:
            raise ValueError(f"vector with name={vector_name} is not valid: {e}") from e
    return vectors, cache


async def _exists_records_with_ids(db: "AsyncSession", dataset_id: UUID, records_ids: List[UUID]) -> List[UUID]:
    result = await db.execute(select(Record.id).filter(Record.dataset_id == dataset_id, Record.id.in_(records_ids)))
    return result.scalars().all()


async def _update_record(
    db: "AsyncSession", dataset: Dataset, record_update: "RecordUpdateWithId", caches: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], Union[List[Suggestion], None], List[VectorSchema], bool, Dict[str, Any]]:
    if caches is None:
        caches = {
            "metadata_properties": {},
            "questions": {},
            "vector_settings": {},
        }

    params = record_update.dict(exclude_unset=True)
    needs_search_engine_update = False
    suggestions = None
    vectors = []

    if "metadata_" in params:
        metadata = params["metadata_"]
        needs_search_engine_update = True
        if metadata is not None:
            caches["metadata_properties"] = await _validate_record_metadata(
                db, dataset, metadata, caches["metadata_properties"]
            )

    if record_update.suggestions is not None:
        params.pop("suggestions")
        questions_ids = [suggestion.question_id for suggestion in record_update.suggestions]
        if len(questions_ids) != len(set(questions_ids)):
            raise ValueError("found duplicate suggestions question IDs")
        suggestions, caches["questions"] = await _build_record_suggestions(db, record_update, caches["questions"])

    if record_update.vectors is not None:
        params.pop("vectors")
        vectors, caches["vector_settings"] = await _build_record_vectors(
            db,
            dataset,
            record_update,
            build_vector_func=lambda value, vector_settings_id: VectorSchema(
                value=value, record_id=record_update.id, vector_settings_id=vector_settings_id
            ),
            cache=caches["vector_settings"],
        )
        needs_search_engine_update = True

    return params, suggestions, vectors, needs_search_engine_update, caches


async def _preload_records_relationships_before_index(db: "AsyncSession", records: List[Record]) -> None:
    for record in records:
        await _preload_record_relationships_before_index(db, record)


async def _preload_record_relationships_before_index(db: "AsyncSession", record: Record) -> None:
    await db.execute(
        select(Record)
        .filter_by(id=record.id)
        .options(
            selectinload(Record.responses).selectinload(Response.user),
            selectinload(Record.suggestions).selectinload(Suggestion.question),
            selectinload(Record.vectors),
        )
    )


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
    caches = {
        "metadata_properties": {},
        "questions": {},
        "vector_settings": {},
    }

    suggestions = []
    upsert_vectors = []
    for record_i, record_update in enumerate(records_update.items):
        try:
            params, record_suggestions, record_vectors, needs_search_engine_update, caches = await _update_record(
                db, dataset, record_update, caches
            )

            if record_suggestions is not None:
                suggestions.extend(record_suggestions)
                records_delete_suggestions.append(record_update.id)

            upsert_vectors.extend(record_vectors)

            if needs_search_engine_update:
                records_search_engine_update.append(record_update.id)

            # Only update the record if there are params to update
            if len(params) > 1:
                records_update_objects.append(params)
        except ValueError as e:
            raise ValueError(f"Record at position {record_i} is not valid because {e}") from e

    async with db.begin_nested():
        if records_delete_suggestions:
            params = [Suggestion.record_id.in_(records_delete_suggestions)]
            await Suggestion.delete_many(db, params=params, autocommit=False)

        if suggestions:
            db.add_all(suggestions)

        if upsert_vectors:
            await Vector.upsert_many(
                db,
                objects=upsert_vectors,
                constraints=[Vector.record_id, Vector.vector_settings_id],
                autocommit=False,
            )

        if records_update_objects:
            await Record.update_many(db, records_update_objects, autocommit=False)

        if records_search_engine_update:
            records = await get_records_by_ids(
                db,
                dataset_id=dataset.id,
                records_ids=records_search_engine_update,
                include=RecordIncludeParam(keys=[RecordInclude.vectors], vectors=None),
            )
            await dataset.awaitable_attrs.vectors_settings
            await _preload_records_relationships_before_index(db, records)
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
    params, suggestions, vectors, needs_search_engine_update, _ = await _update_record(
        db, record.dataset, RecordUpdateWithId(id=record.id, **record_update.dict(by_alias=True, exclude_unset=True))
    )

    # Remove existing suggestions
    if suggestions is not None:
        record.suggestions = []
        params["suggestions"] = suggestions

    async with db.begin_nested():
        record = await record.update(db, **params, replace_dict=True, autocommit=False)

        if vectors:
            await Vector.upsert_many(
                db, objects=vectors, constraints=[Vector.record_id, Vector.vector_settings_id], autocommit=False
            )
            await db.refresh(record, attribute_names=["vectors"])

        if needs_search_engine_update:
            await record.dataset.awaitable_attrs.vectors_settings
            await _preload_record_relationships_before_index(db, record)
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
    _validate_response_values(record.dataset, values=response_create.values, status=response_create.status)

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
    _validate_response_values(response.record.dataset, values=response_update.values, status=response_update.status)

    async with db.begin_nested():
        response = await response.update(
            db,
            values=jsonable_encoder(response_update.values),
            status=response_update.status,
            replace_dict=True,
            autocommit=False,
        )

        await _load_users_from_responses(response)
        await _touch_dataset_last_activity_at(db, response.record.dataset)
        await search_engine.update_record_response(response)

    await db.commit()

    return response


async def upsert_response(
    db: "AsyncSession", search_engine: SearchEngine, record: Record, user: User, response_upsert: ResponseUpsert
) -> Response:
    _validate_response_values(record.dataset, values=response_upsert.values, status=response_upsert.status)

    schema = {
        "values": jsonable_encoder(response_upsert.values),
        "status": response_upsert.status,
        "record_id": response_upsert.record_id,
        "user_id": user.id,
    }

    async with db.begin_nested():
        response = await Response.upsert(
            db,
            schema=schema,
            constraints=[Response.record_id, Response.user_id],
            autocommit=False,
        )

        await _load_users_from_responses(response)
        await _touch_dataset_last_activity_at(db, response.record.dataset)
        await search_engine.update_record_response(response)

    await db.commit()

    return response


async def delete_response(db: "AsyncSession", search_engine: SearchEngine, response: Response) -> Response:
    async with db.begin_nested():
        response = await response.delete(db, autocommit=False)
        await _load_users_from_responses(response)
        await _touch_dataset_last_activity_at(db, response.record.dataset)
        await search_engine.delete_record_response(response)

    await db.commit()

    return response


def _validate_response_values(
    dataset: Dataset,
    values: Union[Dict[str, ResponseValueCreate], Dict[str, ResponseValueUpdate], None],
    status: ResponseStatus,
):
    if not values:
        if status not in [ResponseStatus.discarded, ResponseStatus.draft]:
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


def _validate_record_fields(dataset: Dataset, fields: Dict[str, Any]):
    fields_copy = copy.copy(fields or {})
    for field in dataset.fields:
        if field.required and not (field.name in fields_copy and fields_copy.get(field.name) is not None):
            raise ValueError(f"missing required value for field: {field.name!r}")

        value = fields_copy.pop(field.name, None)
        if value and not isinstance(value, str):
            raise ValueError(
                f"wrong value found for field {field.name!r}. Expected {str.__name__!r}, found {type(value).__name__!r}"
            )

    if fields_copy:
        raise ValueError(f"found fields values for non configured fields: {list(fields_copy.keys())!r}")


async def get_suggestion_by_record_id_and_question_id(
    db: "AsyncSession", record_id: UUID, question_id: UUID
) -> Union[Suggestion, None]:
    result = await db.execute(select(Suggestion).filter_by(record_id=record_id, question_id=question_id))
    return result.scalar_one_or_none()


async def _preload_suggestion_relationships_before_index(db: "AsyncSession", suggestion: Suggestion) -> None:
    await db.execute(
        select(Suggestion)
        .filter_by(id=suggestion.id)
        .options(
            selectinload(Suggestion.record).selectinload(Record.dataset),
            selectinload(Suggestion.question),
        )
    )


async def upsert_suggestion(
    db: "AsyncSession",
    search_engine: SearchEngine,
    record: Record,
    question: Question,
    suggestion_create: "SuggestionCreate",
) -> Suggestion:
    question.parsed_settings.check_response(suggestion_create)

    async with db.begin_nested():
        suggestion = await Suggestion.upsert(
            db,
            schema=SuggestionCreateWithRecordId(record_id=record.id, **suggestion_create.dict()),
            constraints=[Suggestion.record_id, Suggestion.question_id],
            autocommit=False,
        )
        await _preload_suggestion_relationships_before_index(db, suggestion)
        await search_engine.update_record_suggestion(suggestion)

    await db.commit()

    return suggestion


async def delete_suggestions(
    db: "AsyncSession", search_engine: SearchEngine, record: Record, suggestions_ids: List[UUID]
) -> None:
    params = [Suggestion.id.in_(suggestions_ids), Suggestion.record_id == record.id]
    suggestions = await list_suggestions_by_id_and_record_id(db, suggestions_ids, record.id)

    async with db.begin_nested():
        await Suggestion.delete_many(db=db, params=params, autocommit=False)
        for suggestion in suggestions:
            await search_engine.delete_record_suggestion(suggestion)

    await db.commit()


async def get_suggestion_by_id(db: "AsyncSession", suggestion_id: "UUID") -> Union[Suggestion, None]:
    result = await db.execute(
        select(Suggestion)
        .filter_by(id=suggestion_id)
        .options(
            selectinload(Suggestion.record).selectinload(Record.dataset),
            selectinload(Suggestion.question),
        )
    )

    return result.scalar_one_or_none()


async def list_suggestions_by_id_and_record_id(
    db: "AsyncSession", suggestion_ids: List[UUID], record_id: UUID
) -> Sequence[Suggestion]:
    result = await db.execute(
        select(Suggestion)
        .filter(Suggestion.record_id == record_id, Suggestion.id.in_(suggestion_ids))
        .options(
            selectinload(Suggestion.record).selectinload(Record.dataset),
            selectinload(Suggestion.question),
        )
    )

    return result.scalars().all()


async def delete_suggestion(db: "AsyncSession", search_engine: SearchEngine, suggestion: Suggestion) -> Suggestion:
    async with db.begin_nested():
        suggestion = await suggestion.delete(db, autocommit=False)
        await search_engine.delete_record_suggestion(suggestion)

    await db.commit()

    return suggestion


async def get_metadata_property_by_id(db: "AsyncSession", metadata_property_id: UUID) -> Optional[MetadataProperty]:
    result = await db.execute(
        select(MetadataProperty).filter_by(id=metadata_property_id).options(selectinload(MetadataProperty.dataset))
    )
    return result.scalar_one_or_none()
