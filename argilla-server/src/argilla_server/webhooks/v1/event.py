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
from datetime import datetime

from rq.job import Job
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.jobs.webhook_jobs import enqueue_notify_events


class Event:
    def __init__(self, event: str, timestamp: datetime, data: dict):
        self.event = event
        self.timestamp = timestamp
        self.data = data

    async def notify(self, db: AsyncSession) -> List[Job]:
        return await enqueue_notify_events(
            db,
            event=self.event,
            timestamp=self.timestamp,
            data=self.data,
        )
