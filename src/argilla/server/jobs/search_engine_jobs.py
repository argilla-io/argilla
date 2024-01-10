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

from argilla.server.cli.search_engine.reindex import Reindexer
from argilla.server.database import AsyncSessionLocal
from argilla.server.jobs.queues import default_queue
from argilla.server.search_engine.base import SearchEngine
from argilla.server.settings import settings
from rq import Retry
from rq.decorators import job


# NOTE:
# This could be executed as a normal function:
# > await reindex_dataset(UUID("cfcc028a-1669-4b6a-baf5-9b50e0538e44"))
# Or with rq in background:
# > reindex_dataset.delay(UUID("cfcc028a-1669-4b6a-baf5-9b50e0538e44"))
@job(default_queue, retry=Retry(max=3, interval=60))
async def reindex_dataset(dataset_id: UUID):
    async with AsyncSessionLocal() as db, SearchEngine.get_by_name(settings.search_engine) as search_engine:
        dataset = await Reindexer.reindex_dataset(db, search_engine, dataset_id)

        async for records in Reindexer.reindex_dataset_records(db, search_engine, dataset):
            ...
