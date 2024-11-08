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

from rq import Retry
from rq.decorators import job
from sqlalchemy.orm import selectinload

from argilla_server.models import Dataset
from argilla_server.settings import settings
from argilla_server.contexts.hub import HubDataset
from argilla_server.database import AsyncSessionLocal
from argilla_server.search_engine.base import SearchEngine
from argilla_server.api.schemas.v1.datasets import HubDatasetMapping
from argilla_server.jobs.queues import DEFAULT_QUEUE

# TODO: Move this to be defined on jobs queues as a shared constant
JOB_TIMEOUT_DISABLED = -1

HUB_DATASET_TAKE_ROWS = 10_000


# TODO: Once we merge webhooks we should change the queue to use a different one (default queue is deleted there)
@job(DEFAULT_QUEUE, timeout=JOB_TIMEOUT_DISABLED, retry=Retry(max=3))
async def import_dataset_from_hub_job(name: str, subset: str, split: str, dataset_id: UUID, mapping: dict) -> None:
    async with AsyncSessionLocal() as db:
        dataset = await Dataset.get_or_raise(
            db,
            dataset_id,
            options=[
                selectinload(Dataset.fields),
                selectinload(Dataset.questions),
                selectinload(Dataset.metadata_properties),
            ],
        )

        async with SearchEngine.get_by_name(settings.search_engine) as search_engine:
            parsed_mapping = HubDatasetMapping.model_validate(mapping)

            await (
                HubDataset(name, subset, split, parsed_mapping)
                .take(HUB_DATASET_TAKE_ROWS)
                .import_to(db, search_engine, dataset)
            )
