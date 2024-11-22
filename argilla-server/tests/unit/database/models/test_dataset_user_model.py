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

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.models import DatasetUser
from tests.factories import UserFactory, DatasetFactory


@pytest.mark.asyncio
class TestDatasetUserModel:
    async def test_create_duplicated_dataset_user(self, db: AsyncSession):
        user = await UserFactory.create()
        dataset = await DatasetFactory.create()

        db.add_all(
            [
                DatasetUser(user_id=user.id, dataset_id=dataset.id),
                DatasetUser(user_id=user.id, dataset_id=dataset.id),
            ]
        )

        with pytest.raises(
            IntegrityError,
            match="UNIQUE constraint failed: datasets_users.dataset_id, datasets_users.user_id",
        ):
            await db.commit()
