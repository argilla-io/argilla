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

from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.api.policies.v1 import RecordPolicy, authorize
from argilla_server.api.schemas.v1.responses import Response, ResponseBulk, ResponseBulkError, ResponseUpsert
from argilla_server.contexts import datasets
from argilla_server.database import get_async_db
from argilla_server.errors import future as errors
from argilla_server.models import User
from argilla_server.search_engine import SearchEngine, get_search_engine


class UpsertResponsesInBulkUseCase:
    def __init__(self, db: AsyncSession, search_engine: SearchEngine):
        self.db = db
        self.search_engine = search_engine

    async def execute(self, responses: List[ResponseUpsert], user: User) -> List[ResponseBulk]:
        responses_bulk_items = []

        all_records = await datasets.get_records_by_ids(self.db, [item.record_id for item in responses])
        non_empty_records = [r for r in all_records if r is not None]

        await datasets.preload_records_relationships_before_validate(self.db, non_empty_records)
        for item, record in zip(responses, all_records):
            try:
                if record is None:
                    raise errors.NotFoundError(f"Record with id `{item.record_id}` not found")

                await authorize(user, RecordPolicy.create_response(record))

                response = await datasets.upsert_response(self.db, self.search_engine, record, user, item)
            except Exception as err:
                responses_bulk_items.append(ResponseBulk(item=None, error=ResponseBulkError(detail=str(err))))
            else:
                responses_bulk_items.append(ResponseBulk(item=Response.model_validate(response), error=None))

        return responses_bulk_items


class UpsertResponsesInBulkUseCaseFactory:
    def __call__(
        self,
        db: AsyncSession = Depends(get_async_db),
        search_engine: SearchEngine = Depends(get_search_engine),
    ):
        return UpsertResponsesInBulkUseCase(db, search_engine)
