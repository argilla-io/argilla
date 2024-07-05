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

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.database import get_async_db
from argilla_server.models import Dataset


class DatasetsRepository:
    def __init__(self, db: AsyncSession = Depends(get_async_db)):
        self.db = db

    async def get(self, dataset_id: UUID) -> Dataset:
        return await Dataset.get_or_raise(db=self.db, id=dataset_id)
