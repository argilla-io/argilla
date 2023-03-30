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

from argilla.server.commons.models import TaskType
from argilla.server.daos.datasets import DatasetsDAO
from argilla.server.daos.models.datasets import BaseDatasetDB
from argilla.server.security.model import User
from argilla.server.services.datasets import DatasetsService


def test_copy_dataset_with_no_owner_info(datasets_service: DatasetsService, datasets_dao: DatasetsDAO):
    dataset_name = "test_copy_dataset_with_no_owned_dataset"
    dataset_copy_name = f"{dataset_name}_copy"

    dataset = BaseDatasetDB(name=dataset_name, task=TaskType.text_classification)
    user = User(username="test-user")

    datasets_dao.delete_dataset(dataset)
    datasets_dao.delete_dataset(
        BaseDatasetDB(
            name=dataset_copy_name,
            task=TaskType.text_classification,
            owner=user.username,
        )
    )

    datasets_dao.create_dataset(dataset)

    dataset_copy = datasets_service.copy_dataset(user, dataset=dataset, copy_name=dataset_copy_name)

    assert dataset_copy.created_by == user.username
    assert dataset_copy.name == dataset_copy_name
    assert dataset_copy.owner == user.username
