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

from argilla.server.contexts import datasets
from argilla.server.database import AsyncSessionLocal
from argilla.server.search_engine import SearchEngine
from argilla.server.tasks import background_tasks


@background_tasks.task("refresh-search-engine-index")
async def refresh_search_engine_index(engine: str, dataset_id: UUID):
    async with AsyncSessionLocal() as db:
        async with SearchEngine.get_by_name(engine) as engine:
            dataset = await datasets.get_dataset_by_id(db, dataset_id)
            await engine.refresh_index(dataset)
