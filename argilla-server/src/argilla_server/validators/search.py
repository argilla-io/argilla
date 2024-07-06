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

from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.api.schemas.v1.records import (
    SearchRecordsQuery,
    Query,
    VectorQuery,
    FilterScope,
    RecordFilterScope,
    MetadataFilterScope,
)
from argilla_server.api.schemas.v1.responses import ResponseFilterScope
from argilla_server.api.schemas.v1.suggestions import SuggestionFilterScope
from argilla_server.errors.future import NotFoundError, UnprocessableEntityError, MissingVectorError
from argilla_server.errors.future.base_errors import MISSING_VECTOR_ERROR_CODE
from argilla_server.models import VectorSettings, Record, Field, Question, MetadataProperty
from argilla_server.search_engine import TextQuery


class SearchRecordsQueryValidator:
    def __init__(self, db: AsyncSession, query: SearchRecordsQuery, dataset_id: UUID):
        self._db = db
        self._query = query
        self._dataset_id = dataset_id

    async def validate(self) -> None:
        try:
            if self._query.filters:
                for filter in self._query.filters.and_:
                    await self._validate_filter_scope(filter.scope)

            if self._query.sort:
                for order in self._query.sort:
                    await self._validate_filter_scope(order.scope)

            if self._query.query:
                await self._validate_search_query(self._query.query)
        except NotFoundError as ex:
            raise UnprocessableEntityError(str(ex)) from ex

    async def _validate_search_query(self, query: Query):
        if query.text:
            await self._validate_text(query.text)
        if query.vector:
            await self._validate_vector(query.vector)

    async def _validate_vector(self, vector_query: VectorQuery):
        vector_settings = await VectorSettings.get_by(self._db, name=vector_query.name, dataset_id=self._dataset_id)
        if vector_settings is None:
            raise UnprocessableEntityError(f"Vector `{vector_query.name}` not found in dataset `{self._dataset_id}`.")

        if vector_query.record_id is not None:
            record = await Record.get_by(self._db, id=vector_query.record_id, dataset_id=self._dataset_id)
            if record is None:
                raise UnprocessableEntityError(
                    f"Record with id `{vector_query.record_id}` not found in dataset `{self._dataset_id}`."
                )

            await record.awaitable_attrs.vectors

            if not record.vector_value_by_vector_settings(vector_settings):
                # TODO: Once we move to v2.0 we can use here UnprocessableEntityError instead of MissingVectorError
                raise MissingVectorError(
                    message=f"Record `{record.id}` does not have a vector for vector settings `{vector_settings.name}`",
                    code=MISSING_VECTOR_ERROR_CODE,
                )

    async def _validate_text(self, text_query: TextQuery):
        if (
            text_query
            and text_query.field
            and not await Field.get_by(self._db, name=text_query.field, dataset_id=self._dataset_id)
        ):
            raise UnprocessableEntityError(f"Field `{text_query.field}` not found in dataset `{self._dataset_id}`.")

    async def _validate_filter_scope(self, filter_scope: FilterScope) -> None:
        if isinstance(filter_scope, RecordFilterScope):
            return
        elif isinstance(filter_scope, ResponseFilterScope):
            await self._validate_response_filter_scope(filter_scope)
        elif isinstance(filter_scope, SuggestionFilterScope):
            await self._validate_suggestion_filter_scope(filter_scope)
        elif isinstance(filter_scope, MetadataFilterScope):
            await self._validate_metadata_filter_scope(filter_scope)
        else:
            raise ValueError(f"Unknown filter scope entity `{filter_scope.entity}`")

    async def _validate_response_filter_scope(self, filter_scope: ResponseFilterScope) -> None:
        if filter_scope.question is None:
            return

        await Question.get_by_or_raise(self._db, name=filter_scope.question, dataset_id=self._dataset_id)

    async def _validate_suggestion_filter_scope(self, filter_scope: SuggestionFilterScope) -> None:
        await Question.get_by_or_raise(self._db, name=filter_scope.question, dataset_id=self._dataset_id)

    async def _validate_metadata_filter_scope(self, filter_scope: MetadataFilterScope) -> None:
        await MetadataProperty.get_by_or_raise(
            self._db,
            name=filter_scope.metadata_property,
            dataset_id=self._dataset_id,
        )
