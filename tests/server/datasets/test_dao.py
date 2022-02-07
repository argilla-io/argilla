#  coding=utf-8
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

from rubrix.server.commons.errors import ClosedDatasetError
from rubrix.server.commons.es_wrapper import create_es_wrapper
from rubrix.server.datasets.dao import DatasetsDAO
from rubrix.server.datasets.model import DatasetDB
from rubrix.server.tasks.commons import TaskType
from rubrix.server.tasks.commons.dao.dao import dataset_records_dao

es_wrapper = create_es_wrapper()
records = dataset_records_dao(es_wrapper)
dao = DatasetsDAO.get_instance(es_wrapper, records)


def test_retrieve_ownered_dataset_for_no_owner_user():
    dataset = "test_retrieve_ownered_dataset_for_no_owner_user"
    created = dao.create_dataset(
        DatasetDB(name=dataset, owner="other", task=TaskType.text_classification)
    )
    assert dao.find_by_name(created.name, owner=created.owner) == created
    assert dao.find_by_name(created.name, owner=None) == created
    assert dao.find_by_name(created.name, owner="me") is None


def test_close_dataset():
    dataset = "test_close_dataset"

    created = dao.create_dataset(
        DatasetDB(name=dataset, owner="other", task=TaskType.text_classification)
    )

    dao.close(created)
    with pytest.raises(ClosedDatasetError, match=dataset):
        records.search_records(dataset=created)

    dao.open(created)
    records.search_records(dataset=created)
