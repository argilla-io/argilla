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

from collections import defaultdict
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Iterable,
    List,
    Optional,
    Sequence,
    Union,
)
from uuid import UUID

import sqlalchemy
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Select, and_, func, select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from argilla_server.api.schemas.v1.fields import FieldCreate
from argilla_server.api.schemas.v1.metadata_properties import MetadataPropertyCreate, MetadataPropertyUpdate
from argilla_server.api.schemas.v1.records import (
    RecordIncludeParam,
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


async def dataset_has_records(db: AsyncSession, dataset: Dataset) -> bool:
    return bool(await db.scalar(select(exists().where(Record.dataset_id == dataset.id))))


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


# TODO: Move this function to the records.py context
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


async def _load_users_from_responses(responses: Union[Response, Iterable[Response]]) -> None:
    if isinstance(responses, Response):
        responses = [responses]

    # TODO: We should do a single query retrieving all the users from all responses instead of using awaitable_attrs,
    # something similar to what we are already doing in _preload_suggestion_relationships_before_index.
    for response in responses:
        await response.awaitable_attrs.user


async def preload_records_relationships_before_validate(db: AsyncSession, records: List[Record]) -> None:
    await db.execute(
        select(Record)
        .filter(Record.id.in_([record.id for record in records]))
        .options(
            selectinload(Record.dataset).selectinload(Dataset.questions),
        )
    )


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
