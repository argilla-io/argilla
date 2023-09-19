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
