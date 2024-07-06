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

import asyncio
from typing import Any, Dict, Optional, List, Sequence

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import argilla_server.search_engine as search_engine
from argilla_server.api.policies.v1 import is_authorized, RecordPolicy
from argilla_server.api.schemas.v1.records import (
    MetadataFilterScope,
    RangeFilter,
    RecordFilterScope,
    SearchRecord,
    SearchRecordsQuery,
    SearchRecordsResult,
    FilterScope,
    Filters,
    TermsFilter,
    Order,
    RecordIncludeParam,
)
from argilla_server.api.schemas.v1.responses import ResponseFilterScope
from argilla_server.api.schemas.v1.suggestions import (
    SuggestionFilterScope,
)
from argilla_server.contexts import datasets
from argilla_server.validators.search import SearchRecordsQueryValidator
from argilla_server.database import get_async_db
from argilla_server.errors.future import NotFoundError, UnprocessableEntityError
from argilla_server.models import Dataset, User, VectorSettings, Record
from argilla_server.repositories import RecordsRepository, DatasetsRepository
from argilla_server.search_engine import (
    AndFilter,
    SearchEngine,
    get_search_engine,
    SearchResponses,
)


class SearchService:
    def __init__(
        self,
        datasets: DatasetsRepository = Depends(),
        records: RecordsRepository = Depends(),
        db: AsyncSession = Depends(get_async_db),
        engine: SearchEngine = Depends(get_search_engine),
    ):
        self.db = db
        self.engine = engine
        self.records = records
        self.datasets = datasets

    async def search_records(
        self,
        user: User,
        dataset: Dataset,
        search_query: SearchRecordsQuery,
        offset: int,
        limit: int,
        include: Optional[RecordIncludeParam] = None,
        search_bounded_to_user: bool = False,
    ) -> Any:
        dataset = await self.datasets.get(
            dataset.id,
            options=[selectinload(Dataset.fields), selectinload(Dataset.metadata_properties)],
        )

        search_query = search_query or SearchRecordsQuery()
        await SearchRecordsQueryValidator(self.db, search_query, dataset.id).validate()

        if search_query.vector_query:
            results = await self._similarity_search(dataset, search_query, user, max_results=limit)
        else:
            results = await self._search(
                dataset=dataset,
                search_query=search_query,
                offset=offset,
                limit=limit,
                user=user if search_bounded_to_user else None,
            )

        records = await datasets.get_records_by_ids(
            db=self.db,
            dataset_id=dataset.id,
            records_ids=list([r.record_id for r in results.items]),
            include=include,
            user_id=user.id if search_bounded_to_user else None,
        )
        await self._filter_records_metadata_for_user(records, user)

        records_by_id = {record.id: record for record in records}
        return SearchRecordsResult(
            total=results.total,
            items=[
                SearchRecord(record=records_by_id[response.record_id], query_score=response.score)
                for response in results.items
            ],
        )

    async def _similarity_search(
        self, dataset: Dataset, search_query: SearchRecordsQuery, user: User, max_results: int
    ) -> SearchResponses:
        filters = self._to_search_engine_filter(search_query.filters, user=user)

        text_query = search_query.text_query
        vector_query = search_query.vector_query

        vector_settings = await VectorSettings.get_by(self.db, name=vector_query.name, dataset_id=dataset.id)
        record = (await Record.get_by(self.db, id=vector_query.record_id)) if vector_query.record_id else None

        return await self.engine.similarity_search(
            dataset=dataset,
            vector_settings=vector_settings,
            value=vector_query.value,
            record=record,
            query=text_query,
            filter=filters,
            order=vector_query.order,
            max_results=max_results,
        )

    async def _search(
        self,
        dataset: Dataset,
        search_query: SearchRecordsQuery,
        offset: int,
        limit: int,
        user: Optional[User] = None,
    ) -> SearchResponses:
        filters = self._to_search_engine_filter(search_query.filters, user=user)
        sort = self._to_search_engine_sort(search_query.sort, user)
        text_query = search_query.text_query

        return await self.engine.search(
            dataset=dataset,
            query=text_query,
            filter=filters,
            sort=sort,
            user_id=user.id if user else None,
            offset=offset,
            limit=limit,
        )

    async def _filter_records_metadata_for_user(self, records: Sequence[Record], user: User) -> None:
        records_metadata = await asyncio.gather(
            *[self._filter_record_metadata_for_user(record, user) for record in records]
        )

        for record, metadata in zip(records, records_metadata):
            record.metadata_ = metadata

    @staticmethod
    def _to_search_engine_filter_scope(scope: FilterScope, user: Optional[User]) -> search_engine.FilterScope:
        if isinstance(scope, RecordFilterScope):
            return search_engine.RecordFilterScope(property=scope.property.value)
        elif isinstance(scope, MetadataFilterScope):
            return search_engine.MetadataFilterScope(metadata_property=scope.metadata_property)
        elif isinstance(scope, SuggestionFilterScope):
            return search_engine.SuggestionFilterScope(question=scope.question, property=str(scope.property))
        elif isinstance(scope, ResponseFilterScope):
            return search_engine.ResponseFilterScope(question=scope.question, property=scope.property, user=user)
        else:
            raise Exception(f"Unknown scope type {type(scope)}")

    def _to_search_engine_filter(self, filters: Filters, user: Optional[User]) -> Optional[search_engine.Filter]:
        if filters is None:
            return None

        engine_filters = []
        for filter in filters.and_:
            engine_scope = self._to_search_engine_filter_scope(filter.scope, user=user)

            if isinstance(filter, TermsFilter):
                engine_filter = search_engine.TermsFilter(scope=engine_scope, values=filter.values)
            elif isinstance(filter, RangeFilter):
                engine_filter = search_engine.RangeFilter(scope=engine_scope, ge=filter.ge, le=filter.le)
            else:
                raise Exception(f"Unknown filter type {type(filter)}")

            engine_filters.append(engine_filter)

        return AndFilter(filters=engine_filters)

    def _to_search_engine_sort(self, sort: List[Order], user: Optional[User]) -> Optional[List[search_engine.Order]]:
        if sort is None:
            return None

        engine_sort = []
        for order in sort:
            engine_scope = self._to_search_engine_filter_scope(order.scope, user=user)
            engine_sort.append(search_engine.Order(scope=engine_scope, order=order.order))

        return engine_sort

    @staticmethod
    async def _filter_record_metadata_for_user(record: Record, user: User) -> Optional[Dict[str, Any]]:
        if record.metadata_ is None:
            return None

        metadata = {}
        for metadata_name in list(record.metadata_.keys()):
            if await is_authorized(user, RecordPolicy.get_metadata(record, metadata_name)):
                metadata[metadata_name] = record.metadata_[metadata_name]

        return metadata
