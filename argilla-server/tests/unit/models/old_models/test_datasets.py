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
import datetime
import uuid

import pytest
from argilla_server.commons.models import TaskType
from argilla_server.daos.models.datasets import BaseDatasetDB
from argilla_server.schemas.v0.datasets import CreateDatasetRequest, Dataset

from tests.pydantic_v1 import ValidationError


@pytest.mark.parametrize(
    "name",
    ["fine", "fine33", "fine_33", "fine-3-3"],
)
def test_dataset_naming_ok(name):
    request = CreateDatasetRequest(name=name, task=TaskType.token_classification)
    assert request.name == name


@pytest.mark.parametrize(
    "name",
    [
        "WrongName",
        "-wrong_name",
        "_wrong_name",
        "wrong_name-??",
        "wrong name",
        "wrong:name",
        "wrong=?name",
    ],
)
def test_dataset_naming_ko(name):
    with pytest.raises(ValidationError, match="string does not match regex"):
        CreateDatasetRequest(name=name, task=TaskType.token_classification)


@pytest.mark.parametrize(
    ("dataset", "expected_workspace"),
    [
        (BaseDatasetDB(name="ds", workspace="ws", task=TaskType.text_classification), "ws"),
        (BaseDatasetDB(name="ds", owner="owner", task=TaskType.text_classification), "owner"),
        (BaseDatasetDB(name="ds", workspace="ws", owner="owner", task=TaskType.text_classification), "ws"),
        (BaseDatasetDB(name="ds", workspace=None, owner="ws", task=TaskType.text_classification), "ws"),
    ],
)
def test_dataset_creation_sync(dataset, expected_workspace):
    assert dataset.workspace == expected_workspace
    assert dataset.owner == dataset.workspace
    assert dataset.id == f"{dataset.workspace}.{dataset.name}"


def test_dataset_creation_fails_on_no_workspace_and_owner():
    with pytest.raises(ValueError, match="Missing workspace"):
        BaseDatasetDB(task=TaskType.text_classification, name="tedb", workspace=None, owner=None)


def test_accept_create_dataset_without_created_by():
    ds = Dataset(
        name="a-dataset",
        id=uuid.uuid4(),
        task=TaskType.text_classification,
        owner="dd",
        workspace="dd",
        created_at=datetime.datetime.utcnow(),
        last_updated=datetime.datetime.utcnow(),
    )

    assert ds
    assert ds.created_by is None


def test_change_workspace_by_setting():
    dataset = BaseDatasetDB(
        name="a-dataset",
        task=TaskType.text_classification,
        workspace="workspace_name",
        created_at=datetime.datetime.utcnow(),
        last_updated=datetime.datetime.utcnow(),
    )

    assert dataset.workspace == dataset.owner
    dataset.workspace = "another_workspace"

    assert dataset.workspace == dataset.owner
