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

import typer

from typing import List

from argilla_server.jobs.queues import DEFAULT_QUEUE, HIGH_QUEUE

DEFAULT_NUM_WORKERS = 2


def worker(
    queues: List[str] = typer.Option([DEFAULT_QUEUE.name, HIGH_QUEUE.name], help="Name of queues to listen"),
    num_workers: int = typer.Option(DEFAULT_NUM_WORKERS, help="Number of workers to start"),
) -> None:
    from rq.worker_pool import WorkerPool
    from argilla_server.jobs.queues import REDIS_CONNECTION

    worker_pool = WorkerPool(
        connection=REDIS_CONNECTION,
        queues=queues,
        num_workers=num_workers,
    )

    worker_pool.start()
