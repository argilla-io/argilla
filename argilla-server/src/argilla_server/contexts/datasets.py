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
from collections import defaultdict
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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from argilla_server.api.schemas.v1.fields import FieldCreate
from argilla_server.api.schemas.v1.metadata_properties import MetadataPropertyCreate, MetadataPropertyUpdate
from argilla_server.api.schemas.v1.records import (
    RecordCreate,
    RecordIncludeParam,
    RecordUpdateWithId,
)
from argilla_server.api.schemas.v1.responses import (
    ResponseCreate,
    ResponseUpdate,
    ResponseUpsert,
)
from argilla_server.api.schemas.v1.vector_settings import (
    VectorSettings as VectorSettingsSchema,
)
from argilla_server.api.schemas.v1.vector_settings import (
    VectorSettingsCreate,
)
from argilla_server.api.schemas.v1.vectors import Vector as VectorSchema
from argilla_server.models.database import DatasetUser
from argilla_server.webhooks.v1.enums import DatasetEvent, ResponseEvent, RecordEvent
from argilla_server.webhooks.v1.records import (
    build_record_event as build_record_event_v1,
    notify_record_event as notify_record_event_v1,
)
from argilla_server.webhooks.v1.responses import (
    build_response_event as build_response_event_v1,
    notify_response_event as notify_response_event_v1,
)
from argilla_server.webhooks.v1.datasets import (
    build_dataset_event as build_dataset_event_v1,
    notify_dataset_event as notify_dataset_event_v1,
)
from argilla_server.contexts import accounts, distribution
from argilla_server.database import get_async_db
from argilla_server.enums import DatasetStatus, UserRole
from argilla_server.errors.future import NotUniqueError, UnprocessableEntityError
from argilla_server.jobs import dataset_jobs
from argilla_server.models import (
    Dataset,
    Field,
    MetadataProperty,
    Question,
    Record,
    Response,
    Suggestion,
    User,
    Vector,
    VectorSettings,
    WorkspaceUser,
)
from argilla_server.models.suggestions import SuggestionCreateWithRecordId
from argilla_server.search_engine import SearchEngine
from argilla_server.validators.datasets import DatasetCreateValidator, DatasetPublishValidator, DatasetUpdateValidator
from argilla_server.validators.responses import (
    ResponseCreateValidator,
    ResponseUpdateValidator,
    ResponseUpsertValidator,
)
from argilla_server.validators.suggestions import SuggestionCreateValidator

if TYPE_CHECKING:
    from argilla_server.api.schemas.v1.fields import FieldUpdate
    from argilla_server.api.schemas.v1.records import RecordUpdate
    from argilla_server.api.schemas.v1.suggestions import SuggestionCreate
    from argilla_server.api.schemas.v1.vector_settings import VectorSettingsUpdate

VISIBLE_FOR_ANNOTATORS_ALLOWED_ROLES = [UserRole.admin, UserRole.annotator]
NOT_VISIBLE_FOR_ANNOTATORS_ALLOWED_ROLES = [UserRole.admin]

CREATE_DATASET_VECTOR_SETTINGS_MAX_COUNT = 5


async def _touch_dataset_last_activity_at(db: AsyncSession, dataset: Dataset) -> None:
    await db.execute(
        sqlalchemy.update(Dataset)
        .where(Dataset.id == dataset.id)
        .values(
            last_activity_at=datetime.utcnow(),
            updated_at=Dataset.__table__.c.updated_at,
        )
    )


async def list_datasets(db: AsyncSession, user: Optional[User] = None, **filters) -> Sequence[Dataset]:
    """
    List stored datasets. If `user` is provided, only datasets available to the user will be returned.
    Additionally, filters based on `Dataset` class attributes can be applied

    """
    query = select(Dataset).filter_by(**filters).order_by(Dataset.inserted_at.asc())

    if user and not user.is_owner:
        query = query.join(
            WorkspaceUser,
            and_(
                WorkspaceUser.workspace_id == Dataset.workspace_id,
                WorkspaceUser.user_id == user.id,
            ),
        )

    result = await db.scalars(query)

    return result.all()


async def list_datasets_by_workspace_id(db: AsyncSession, workspace_id: UUID) -> Sequence[Dataset]:
    result = await db.execute(
        select(Dataset).where(Dataset.workspace_id == workspace_id).order_by(Dataset.inserted_at.asc())
    )
    return result.scalars().all()


async def create_dataset(db: AsyncSession, dataset_attrs: dict) -> Dataset:
    dataset = Dataset(
        name=dataset_attrs["name"],
        guidelines=dataset_attrs["guidelines"],
        allow_extra_metadata=dataset_attrs["allow_extra_metadata"],
        distribution=dataset_attrs["distribution"],
        metadata_=dataset_attrs["metadata"],
        workspace_id=dataset_attrs["workspace_id"],
    )

    await DatasetCreateValidator.validate(db, dataset)

    await dataset.save(db)

    await notify_dataset_event_v1(db, DatasetEvent.created, dataset)

    return dataset


def _allowed_roles_for_metadata_property_create(metadata_property_create: MetadataPropertyCreate) -> List[UserRole]:
    if metadata_property_create.visible_for_annotators:
        return VISIBLE_FOR_ANNOTATORS_ALLOWED_ROLES
    else:
        return NOT_VISIBLE_FOR_ANNOTATORS_ALLOWED_ROLES


async def publish_dataset(db: AsyncSession, search_engine: SearchEngine, dataset: Dataset) -> Dataset:
    await DatasetPublishValidator.validate(db, dataset)

    dataset = await dataset.update(db, status=DatasetStatus.ready)

    await search_engine.create_index(dataset)

    await notify_dataset_event_v1(db, DatasetEvent.published, dataset)

    return dataset


async def update_dataset(db: AsyncSession, dataset: Dataset, dataset_attrs: dict) -> Dataset:
    await DatasetUpdateValidator.validate(db, dataset, dataset_attrs)

    dataset = await dataset.update(db, **dataset_attrs)

    dataset_jobs.update_dataset_records_status_job.delay(dataset.id)

    await notify_dataset_event_v1(db, DatasetEvent.updated, dataset)

    return dataset


async def delete_dataset(db: AsyncSession, search_engine: SearchEngine, dataset: Dataset) -> Dataset:
    deleted_dataset_event_v1 = await build_dataset_event_v1(db, DatasetEvent.deleted, dataset)

    dataset = await dataset.delete(db)

    await search_engine.delete_index(dataset)
    await deleted_dataset_event_v1.notify(db)

    return dataset


async def create_field(db: AsyncSession, dataset: Dataset, field_create: FieldCreate) -> Field:
    if dataset.is_ready:
        raise UnprocessableEntityError("Field cannot be created for a published dataset")

    if await Field.get_by(db, name=field_create.name, dataset_id=dataset.id):
        raise NotUniqueError(f"Field with name `{field_create.name}` already exists for dataset with id `{dataset.id}`")

    return await Field.create(
        db,
        name=field_create.name,
        title=field_create.title,
        required=field_create.required,
        settings=field_create.settings.model_dump(),
        dataset_id=dataset.id,
    )


async def update_field(db: AsyncSession, field: Field, field_update: "FieldUpdate") -> Field:
    if field_update.settings and field_update.settings.type != field.settings["type"]:
        raise UnprocessableEntityError(
            f"Field type cannot be changed. Expected '{field.settings['type']}' but got '{field_update.settings.type}'"
        )

    params = field_update.model_dump(exclude_unset=True)
    return await field.update(db, **params)


async def delete_field(db: AsyncSession, field: Field) -> Field:
    if field.dataset.is_ready:
        raise UnprocessableEntityError("Fields cannot be deleted for a published dataset")

    return await field.delete(db)


async def delete_metadata_property(db: AsyncSession, metadata_property: MetadataProperty) -> MetadataProperty:
    return await metadata_property.delete(db)


async def create_metadata_property(
    db: AsyncSession,
    search_engine: "SearchEngine",
    dataset: Dataset,
    metadata_property_create: MetadataPropertyCreate,
) -> MetadataProperty:
    if await MetadataProperty.get_by(db, name=metadata_property_create.name, dataset_id=dataset.id):
        raise NotUniqueError(
            f"Metadata property with name `{metadata_property_create.name}` already exists "
            f"for dataset with id `{dataset.id}`"
        )

    metadata_property = await MetadataProperty.create(
        db,
        name=metadata_property_create.name,
        title=metadata_property_create.title,
        settings=metadata_property_create.settings.model_dump(),
        allowed_roles=_allowed_roles_for_metadata_property_create(metadata_property_create),
        dataset_id=dataset.id,
    )

    if dataset.is_ready:
        await search_engine.configure_metadata_property(dataset, metadata_property)

    return metadata_property


async def update_metadata_property(
    db: AsyncSession,
    metadata_property: MetadataProperty,
    metadata_property_update: MetadataPropertyUpdate,
):
    return await metadata_property.update(
        db,
        title=metadata_property_update.title or metadata_property.title,
        allowed_roles=_allowed_roles_for_metadata_property_create(metadata_property_update),
    )


async def count_vectors_settings_by_dataset_id(db: AsyncSession, dataset_id: UUID) -> int:
    return (await db.execute(select(func.count(VectorSettings.id)).filter_by(dataset_id=dataset_id))).scalar_one()


async def update_vector_settings(
    db: AsyncSession, vector_settings: VectorSettings, vector_settings_update: "VectorSettingsUpdate"
) -> VectorSettings:
    params = vector_settings_update.model_dump(exclude_unset=True)
    return await vector_settings.update(db, **params)


async def delete_vector_settings(db: AsyncSession, vector_settings: VectorSettings) -> VectorSettings:
    # TODO: for now the search engine does not allow to delete vector settings
    return await vector_settings.delete(db)


async def create_vector_settings(
    db: AsyncSession, search_engine: "SearchEngine", dataset: Dataset, vector_settings_create: "VectorSettingsCreate"
) -> VectorSettings:
    if await count_vectors_settings_by_dataset_id(db, dataset.id) >= CREATE_DATASET_VECTOR_SETTINGS_MAX_COUNT:
        raise UnprocessableEntityError(
            f"The maximum number of vector settings has been reached for dataset with id `{dataset.id}`"
        )

    if await VectorSettings.get_by(db, name=vector_settings_create.name, dataset_id=dataset.id):
        raise NotUniqueError(
            f"Vector settings with name `{vector_settings_create.name}` already exists "
            f"for dataset with id `{dataset.id}`"
        )

    vector_settings = await VectorSettings.create(
        db,
        name=vector_settings_create.name,
        title=vector_settings_create.title,
        dimensions=vector_settings_create.dimensions,
        dataset_id=dataset.id,
    )

    if dataset.is_ready:
        await search_engine.configure_index_vectors(vector_settings)

    return vector_settings


async def get_records_by_ids(
    db: AsyncSession,
    records_ids: Iterable[UUID],
    dataset_id: Optional[UUID] = None,
    include: Optional["RecordIncludeParam"] = None,
    user_id: Optional[UUID] = None,
) -> List[Union[Record, None]]:
    query = select(Record)

    if dataset_id:
        query.filter(Record.dataset_id == dataset_id)

    query = query.filter(Record.id.in_(records_ids))

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
    ordered_records = [record_order_map.get(record_id, None) for record_id in records_ids]

    return ordered_records


async def _configure_query_relationships(
    query: Select, dataset_id: UUID, include_params: Optional["RecordIncludeParam"] = None
) -> Select:
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


async def get_user_dataset_metrics(
    db: AsyncSession,
    search_engine: SearchEngine,
    user: User,
    dataset: Dataset,
) -> dict:
    total_records = (await get_dataset_progress(db, search_engine, dataset))["total"]
    result = await search_engine.get_dataset_user_progress(dataset, user)

    submitted_responses = result.get("submitted", 0)
    discarded_responses = result.get("discarded", 0)
    draft_responses = result.get("draft", 0)
    pending_responses = total_records - submitted_responses - discarded_responses - draft_responses

    return {
        "total": total_records,
        "submitted": submitted_responses,
        "discarded": discarded_responses,
        "draft": draft_responses,
        "pending": pending_responses,
    }


async def get_dataset_progress(
    db: AsyncSession,
    search_engine: SearchEngine,
    dataset: Dataset,
) -> dict:
    result = await search_engine.get_dataset_progress(dataset)
    users = await get_users_with_responses_for_dataset(db, dataset)

    return {
        "total": result.get("total", 0),
        "completed": result.get("completed", 0),
        "pending": result.get("pending", 0),
        "users": users,
    }


async def get_users_with_responses_for_dataset(
    db: AsyncSession,
    dataset: Dataset,
) -> Sequence[User]:
    query = (
        select(DatasetUser)
        .filter_by(dataset_id=dataset.id)
        .options(selectinload(DatasetUser.user))
        .order_by(DatasetUser.inserted_at.asc())
    )

    result = await db.scalars(query)
    return [r.user for r in result.all()]


async def get_dataset_users_progress(db: AsyncSession, dataset: Dataset) -> List[dict]:
    query = (
        select(User.username, Record.status, Response.status, func.count(Response.id))
        .join(Record)
        .join(User)
        .where(Record.dataset_id == dataset.id)
        .group_by(User.username, Record.status, Response.status)
    )

    annotators_progress = defaultdict(lambda: defaultdict(dict))
    results = (await db.execute(query)).all()

    for username, record_status, response_status, count in results:
        annotators_progress[username][record_status][response_status] = count

    return [{"username": username, **progress} for username, progress in annotators_progress.items()]


_EXTRA_METADATA_FLAG = "extra"


async def _validate_metadata(
    db: AsyncSession,
    dataset: Dataset,
    metadata: Dict[str, Any],
    metadata_properties: Optional[Dict[str, Union[MetadataProperty, Literal["extra"]]]] = None,
) -> Dict[str, Union[MetadataProperty, Literal["extra"]]]:
    if metadata_properties is None:
        metadata_properties = {}

    for name, value in metadata.items():
        metadata_property = metadata_properties.get(name)

        if metadata_property is None:
            metadata_property = await MetadataProperty.get_by(db, name=name, dataset_id=dataset.id)

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
            if value is not None:
                metadata_property.parsed_settings.check_metadata(value)
        except (UnprocessableEntityError, ValueError) as e:
            raise UnprocessableEntityError(f"'{name}' metadata property validation failed because {e}") from e

    return metadata_properties


async def validate_user_exists(db: AsyncSession, user_id: UUID, users_ids: Optional[Set[UUID]]) -> Set[UUID]:
    if not users_ids:
        users_ids = set()

    if user_id not in users_ids:
        if not await accounts.user_exists(db, user_id):
            raise UnprocessableEntityError(f"user_id={str(user_id)} does not exist")

        users_ids.add(user_id)

    return users_ids


async def _validate_vector(
    db: AsyncSession,
    dataset_id: UUID,
    vector_name: str,
    vector_value: List[float],
    vectors_settings: Optional[Dict[str, VectorSettingsSchema]] = None,
) -> Dict[str, VectorSettingsSchema]:
    if vectors_settings is None:
        vectors_settings = {}

    vector_settings = vectors_settings.get(vector_name, None)
    if not vector_settings:
        vector_settings = await VectorSettings.get_by(db, name=vector_name, dataset_id=dataset_id)
        if not vector_settings:
            raise UnprocessableEntityError(
                f"vector with name={str(vector_name)} does not exist for dataset_id={str(dataset_id)}"
            )

        vector_settings = VectorSettingsSchema.model_validate(vector_settings)
        vectors_settings[vector_name] = vector_settings

    vector_settings.check_vector(vector_value)

    return vectors_settings


async def _build_record(
    db: AsyncSession, dataset: Dataset, record_create: RecordCreate, caches: Dict[str, Any]
) -> Record:
    _validate_record_fields(dataset, fields=record_create.fields)
    await _validate_record_metadata(db, dataset, record_create.metadata, caches["metadata_properties_cache"])

    return Record(
        fields=jsonable_encoder(record_create.fields),
        metadata_=record_create.metadata,
        external_id=record_create.external_id,
        dataset=dataset,
    )


async def _load_users_from_responses(responses: Union[Response, Iterable[Response]]) -> None:
    if isinstance(responses, Response):
        responses = [responses]

    # TODO: We should do a single query retrieving all the users from all responses instead of using awaitable_attrs,
    # something similar to what we are already doing in _preload_suggestion_relationships_before_index.
    for response in responses:
        await response.awaitable_attrs.user


async def _validate_record_metadata(
    db: AsyncSession,
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
    except (UnprocessableEntityError, ValueError) as e:
        raise UnprocessableEntityError(f"metadata is not valid: {e}") from e


async def _build_record_suggestions(
    db: AsyncSession,
    record: Record,
    suggestions_create: Optional[List["SuggestionCreate"]],
    questions_cache: Optional[Dict[UUID, Question]] = None,
) -> List[Suggestion]:
    """Create suggestions for a record."""
    if not suggestions_create:
        return []

    suggestions = []
    for suggestion_create in suggestions_create:
        try:
            if not questions_cache:
                questions_cache = {}

            question = questions_cache.get(suggestion_create.question_id, None)
            if not question:
                question = await Question.get(
                    db, suggestion_create.question_id, options=[selectinload(Question.dataset)]
                )
                if not question:
                    raise UnprocessableEntityError(f"question_id={str(suggestion_create.question_id)} does not exist")
                questions_cache[suggestion_create.question_id] = question

            SuggestionCreateValidator.validate(suggestion_create, question.parsed_settings, record)

            suggestions.append(
                Suggestion(
                    type=suggestion_create.type,
                    score=suggestion_create.score,
                    value=jsonable_encoder(suggestion_create.value),
                    agent=suggestion_create.agent,
                    question_id=suggestion_create.question_id,
                    record=record,
                )
            )

        except (UnprocessableEntityError, ValueError) as e:
            raise UnprocessableEntityError(
                f"suggestion for question_id={suggestion_create.question_id} is not valid: {e}"
            ) from e

    return suggestions


VectorClass = TypeVar("VectorClass")


async def _build_record_vectors(
    db: AsyncSession,
    dataset: Dataset,
    vectors_dict: Dict[str, List[float]],
    build_vector_func: Callable[[List[float], UUID], VectorClass],
    cache: Optional[Dict[str, VectorSettingsSchema]] = None,
) -> List[VectorClass]:
    """Create vectors for a record."""
    if not vectors_dict:
        return []

    vectors = []
    for vector_name, vector_value in vectors_dict.items():
        try:
            cache = await _validate_vector(db, dataset.id, vector_name, vector_value, vectors_settings=cache)
            vectors.append(build_vector_func(vector_value, cache[vector_name].id))
        except (UnprocessableEntityError, ValueError) as e:
            raise UnprocessableEntityError(f"vector with name={vector_name} is not valid: {e}") from e

    return vectors


async def _exists_records_with_ids(db: AsyncSession, dataset_id: UUID, records_ids: List[UUID]) -> List[UUID]:
    result = await db.execute(select(Record.id).filter(Record.dataset_id == dataset_id, Record.id.in_(records_ids)))
    return result.scalars().all()


async def _build_record_update(
    db: AsyncSession, record: Record, record_update: "RecordUpdateWithId", caches: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], Union[List[Suggestion], None], List[VectorSchema], bool, Dict[str, Any]]:
    if caches is None:
        caches = {
            "metadata_properties": {},
            "questions": {},
            "vector_settings": {},
        }

    params = record_update.model_dump(exclude_unset=True)
    needs_search_engine_update = False
    suggestions = None
    vectors = []

    if "metadata_" in params:
        metadata = params["metadata_"]
        needs_search_engine_update = True
        if metadata is not None:
            caches["metadata_properties"] = await _validate_record_metadata(
                db, record.dataset, metadata, caches["metadata_properties"]
            )

    if record_update.suggestions is not None:
        params.pop("suggestions")
        questions_ids = [suggestion.question_id for suggestion in record_update.suggestions]
        if len(questions_ids) != len(set(questions_ids)):
            raise UnprocessableEntityError("found duplicate suggestions question IDs")
        suggestions = await _build_record_suggestions(db, record, record_update.suggestions, caches["questions"])

    if record_update.vectors is not None:
        params.pop("vectors")
        vectors = await _build_record_vectors(
            db,
            record.dataset,
            record_update.vectors,
            build_vector_func=lambda value, vector_settings_id: VectorSchema(
                value=value, record_id=record_update.id, vector_settings_id=vector_settings_id
            ),
            cache=caches["vector_settings"],
        )
        needs_search_engine_update = True

    return params, suggestions, vectors, needs_search_engine_update, caches


async def _preload_records_relationships_before_index(db: AsyncSession, records: List[Record]) -> None:
    for record in records:
        await _preload_record_relationships_before_index(db, record)


async def _preload_record_relationships_before_index(db: AsyncSession, record: Record) -> None:
    await db.execute(
        select(Record)
        .filter_by(id=record.id)
        .options(
            selectinload(Record.responses).selectinload(Response.user),
            selectinload(Record.suggestions).selectinload(Suggestion.question),
            selectinload(Record.vectors),
        )
    )


async def preload_records_relationships_before_validate(db: AsyncSession, records: List[Record]) -> None:
    await db.execute(
        select(Record)
        .filter(Record.id.in_([record.id for record in records]))
        .options(
            selectinload(Record.dataset).selectinload(Dataset.questions),
        )
    )


async def delete_records(
    db: AsyncSession, search_engine: "SearchEngine", dataset: Dataset, records_ids: List[UUID]
) -> None:
    params = [Record.id.in_(records_ids), Record.dataset_id == dataset.id]

    records = (await db.execute(select(Record).filter(*params).order_by(Record.inserted_at.asc()))).scalars().all()

    deleted_record_events_v1 = []
    for record in records:
        deleted_record_events_v1.append(
            await build_record_event_v1(db, RecordEvent.deleted, record),
        )

    records = await Record.delete_many(db, conditions=params)

    await search_engine.delete_records(dataset=dataset, records=records)

    for deleted_record_event_v1 in deleted_record_events_v1:
        await deleted_record_event_v1.notify(db)


async def update_record(
    db: AsyncSession, search_engine: "SearchEngine", record: Record, record_update: "RecordUpdate"
) -> Record:
    params, suggestions, vectors, needs_search_engine_update, _ = await _build_record_update(
        db, record, RecordUpdateWithId(id=record.id, **record_update.model_dump(by_alias=True, exclude_unset=True))
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

    await db.commit()

    if needs_search_engine_update:
        await _preload_record_relationships_before_index(db, record)
        await search_engine.index_records(record.dataset, [record])

    await notify_record_event_v1(db, RecordEvent.updated, record)

    return record


async def delete_record(db: AsyncSession, search_engine: "SearchEngine", record: Record) -> Record:
    deleted_record_event_v1 = await build_record_event_v1(db, RecordEvent.deleted, record)

    record = await record.delete(db)

    await search_engine.delete_records(dataset=record.dataset, records=[record])
    await deleted_record_event_v1.notify(db)

    return record


async def create_response(
    db: AsyncSession, search_engine: SearchEngine, record: Record, user: User, response_create: ResponseCreate
) -> Response:
    if await Response.get_by(db, record_id=record.id, user_id=user.id):
        raise NotUniqueError(
            f"Response already exists for record with id `{record.id}` and by user with id `{user.id}`"
        )

    ResponseCreateValidator.validate(response_create, record)

    response = await Response.create(
        db,
        values=jsonable_encoder(response_create.values),
        status=response_create.status,
        record_id=record.id,
        user_id=user.id,
        autocommit=False,
    )
    await _touch_dataset_last_activity_at(db, record.dataset)
    await DatasetUser.upsert(
        db,
        schema={"dataset_id": record.dataset_id, "user_id": user.id},
        constraints=[DatasetUser.dataset_id, DatasetUser.user_id],
        autocommit=False,
    )

    await db.commit()

    await distribution.update_record_status(search_engine, record.id)

    await _load_users_from_responses([response])
    await search_engine.update_record_response(response)

    await notify_response_event_v1(db, ResponseEvent.created, response)

    return response


async def update_response(
    db: AsyncSession, search_engine: SearchEngine, response: Response, response_update: ResponseUpdate
):
    ResponseUpdateValidator.validate(response_update, response.record)

    response = await response.update(
        db,
        values=jsonable_encoder(response_update.values),
        status=response_update.status,
        replace_dict=True,
        autocommit=False,
    )
    await _touch_dataset_last_activity_at(db, response.record.dataset)

    await db.commit()

    await distribution.update_record_status(search_engine, response.record_id)

    await _load_users_from_responses(response)
    await search_engine.update_record_response(response)

    await notify_response_event_v1(db, ResponseEvent.updated, response)

    return response


async def upsert_response(
    db: AsyncSession, search_engine: SearchEngine, record: Record, user: User, response_upsert: ResponseUpsert
) -> Response:
    ResponseUpsertValidator.validate(response_upsert, record)

    response = await Response.upsert(
        db,
        schema={
            "values": jsonable_encoder(response_upsert.values),
            "status": response_upsert.status,
            "record_id": response_upsert.record_id,
            "user_id": user.id,
        },
        constraints=[Response.record_id, Response.user_id],
        autocommit=False,
    )
    await _touch_dataset_last_activity_at(db, response.record.dataset)
    await DatasetUser.upsert(
        db,
        schema={"dataset_id": record.dataset_id, "user_id": user.id},
        constraints=[DatasetUser.dataset_id, DatasetUser.user_id],
        autocommit=False,
    )
    await db.commit()

    await distribution.update_record_status(search_engine, record.id)

    await _load_users_from_responses(response)
    await search_engine.update_record_response(response)

    if response.inserted_at == response.updated_at:
        await notify_response_event_v1(db, ResponseEvent.created, response)
    else:
        await notify_response_event_v1(db, ResponseEvent.updated, response)

    return response


async def delete_response(db: AsyncSession, search_engine: SearchEngine, response: Response) -> Response:
    deleted_response_event_v1 = await build_response_event_v1(db, ResponseEvent.deleted, response)

    response = await response.delete(db, autocommit=False)
    await _touch_dataset_last_activity_at(db, response.record.dataset)

    await db.commit()

    await distribution.update_record_status(search_engine, response.record_id)

    await _load_users_from_responses(response)
    await search_engine.delete_record_response(response)

    await deleted_response_event_v1.notify(db)

    return response


def _validate_record_fields(dataset: Dataset, fields: Dict[str, Any]):
    fields_copy = copy.copy(fields or {})
    for field in dataset.fields:
        if field.required and not (field.name in fields_copy and fields_copy.get(field.name) is not None):
            raise UnprocessableEntityError(f"missing required value for field: {field.name!r}")

        value = fields_copy.pop(field.name, None)
        if value and not isinstance(value, str):
            raise UnprocessableEntityError(
                f"wrong value found for field {field.name!r}. Expected {str.__name__!r}, found {type(value).__name__!r}"
            )

    if fields_copy:
        raise UnprocessableEntityError(f"found fields values for non configured fields: {list(fields_copy.keys())!r}")


async def _preload_suggestion_relationships_before_index(db: AsyncSession, suggestion: Suggestion) -> None:
    await db.execute(
        select(Suggestion)
        .filter_by(id=suggestion.id)
        .options(
            selectinload(Suggestion.record).selectinload(Record.dataset),
            selectinload(Suggestion.question),
        )
    )


async def upsert_suggestion(
    db: AsyncSession,
    search_engine: SearchEngine,
    record: Record,
    question: Question,
    suggestion_create: "SuggestionCreate",
) -> Suggestion:
    SuggestionCreateValidator.validate(suggestion_create, question.parsed_settings, record)

    suggestion = await Suggestion.upsert(
        db,
        schema=SuggestionCreateWithRecordId(record_id=record.id, **suggestion_create.model_dump()),
        constraints=[Suggestion.record_id, Suggestion.question_id],
    )

    await _preload_suggestion_relationships_before_index(db, suggestion)
    await search_engine.update_record_suggestion(suggestion)

    return suggestion


async def delete_suggestions(
    db: AsyncSession, search_engine: SearchEngine, record: Record, suggestions_ids: List[UUID]
) -> None:
    suggestions = await list_suggestions_by_id_and_record_id(db, suggestions_ids, record.id)

    await Suggestion.delete_many(
        db=db,
        conditions=[Suggestion.id.in_(suggestions_ids), Suggestion.record_id == record.id],
    )

    for suggestion in suggestions:
        await search_engine.delete_record_suggestion(suggestion)


async def list_suggestions_by_id_and_record_id(
    db: AsyncSession, suggestion_ids: List[UUID], record_id: UUID
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


async def delete_suggestion(db: AsyncSession, search_engine: SearchEngine, suggestion: Suggestion) -> Suggestion:
    suggestion = await suggestion.delete(db)

    await search_engine.delete_record_suggestion(suggestion)

    return suggestion
