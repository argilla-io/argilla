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
from uuid import UUID

from argilla.server.contexts import datasets
from argilla.server.database import AsyncSessionLocal
from argilla.server.search_engine import SearchEngine
from argilla.server.tasks.base import BackgroundTasks


@BackgroundTasks.task("refresh_search_index")
def refresh_search_index(engine: str, dataset_id: UUID):
    async def _refresh_search_index(engine: str, dataset_id: UUID):
        print(f"Refreshing index for engine {engine} and dataset_id:{dataset_id}")
        async with AsyncSessionLocal() as db:
            async with SearchEngine.get_by_name(engine) as engine:
                try:
                    print(f"Fetching dataset by id {dataset_id}")
                    dataset = await datasets.get_dataset_by_id(
                        db,
                        dataset_id,
                        with_fields=True,
                        with_questions=True,
                        with_vectors_settings=True,
                    )
                    print("Refreshing search engine index")
                    await engine.refresh_index(dataset)
                except Exception as ex:
                    print("Error running index refresh", ex)
                finally:
                    print("Done!")

    asyncio.run(_refresh_search_index(engine, dataset_id))
