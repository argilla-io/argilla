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
from argilla_server.commons.models import TaskType
from argilla_server.daos.backend import GenericElasticEngineBackend
from argilla_server.daos.datasets import DatasetsDAO
from argilla_server.daos.models.datasets import BaseDatasetDB
from argilla_server.daos.records import DatasetRecordsDAO
from argilla_server.errors import ClosedDatasetError

es_wrapper = GenericElasticEngineBackend.get_instance()
records = DatasetRecordsDAO.get_instance(es_wrapper)
dao = DatasetsDAO.get_instance(es_wrapper, records)


def test_retrieve_ownered_dataset_for_no_owner_user():
    dataset = "test_retrieve_owned_dataset_for_no_owner_user"
    created = dao.create_dataset(
        BaseDatasetDB(name=dataset, workspace="other", task=TaskType.text_classification),
    )
    assert dao.find_by_name(created.name, workspace=created.workspace) == created
    assert dao.find_by_name(created.name, workspace="me") is None


def test_list_datasets_by_task():
    dataset = "test_list_datasets_by_task"
    workspace_name = "other"

    all_datasets = dao.list_datasets(workspaces=[workspace_name])
    for ds in all_datasets:
        dao.delete_dataset(ds)

    created_text = dao.create_dataset(
        BaseDatasetDB(
            name=dataset + "_text",
            workspace=workspace_name,
            task=TaskType.text_classification,
        ),
    )

    created_token = dao.create_dataset(
        BaseDatasetDB(
            name=dataset + "_token",
            workspace=workspace_name,
            task=TaskType.token_classification,
        ),
    )

    assert len(dao.list_datasets()) == 0
    assert len(dao.list_datasets(workspaces=[workspace_name])) == 2

    datasets = dao.list_datasets(workspaces=[workspace_name], task2dataset_map={created_text.task: BaseDatasetDB})

    assert len(datasets) == 1
    assert datasets[0].name == created_text.name

    datasets = dao.list_datasets(workspaces=[workspace_name], task2dataset_map={created_token.task: BaseDatasetDB})

    assert len(datasets) == 1
    assert datasets[0].name == created_token.name


def test_close_dataset():
    dataset = "test_close_dataset"

    created = dao.create_dataset(
        BaseDatasetDB(name=dataset, workspace="other", task=TaskType.text_classification),
    )

    dao.close(created)
    with pytest.raises(ClosedDatasetError, match=dataset):
        records.search_records(dataset=created)

    dao.open(created)
    records.search_records(dataset=created)
