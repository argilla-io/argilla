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

import time

import argilla
import pytest
from argilla.client.client import Argilla
from argilla.client.sdk.commons.errors import ForbiddenApiError

from tests.factories import WorkspaceUserFactory


def test_delete_records_from_dataset(mocked_client):
    dataset = "test_delete_records_from_dataset"
    import argilla as rg

    rg.delete(dataset)
    rg.log(
        name=dataset,
        records=[
            rg.TextClassificationRecord(id=i, text="This is the text", metadata=dict(idx=i)) for i in range(0, 50)
        ],
    )

    matched, processed = rg.delete_records(name=dataset, ids=[10], discard_only=True)
    assert matched, processed == (1, 1)

    ds = rg.load(name=dataset)
    assert len(ds) == 50

    time.sleep(1)
    matched, processed = rg.delete_records(name=dataset, query="id:10", discard_only=False)
    assert matched, processed == (1, 1)

    time.sleep(1)
    ds = rg.load(name=dataset)
    assert len(ds) == 49


def test_delete_records_without_permission(mocked_client, argilla_user, mock_user):
    dataset = "test_delete_records_without_permission"

    for workspace in argilla_user.workspaces:
        WorkspaceUserFactory.create(workspace_id=workspace.id, user_id=mock_user.id)

    argilla_client = Argilla()

    argilla_client.delete(dataset)
    argilla_client.log(
        name=dataset,
        records=[
            argilla.TextClassificationRecord(id=i, text="This is the text", metadata=dict(idx=i)) for i in range(0, 50)
        ],
    )
    matched, processed = argilla_client.delete_records(
        name=dataset,
        ids=[10],
        discard_only=True,
    )
    assert matched, processed == (1, 1)

    argilla_client = Argilla(api_key=mock_user.api_key, workspace="argilla")
    with pytest.raises(ForbiddenApiError):
        argilla_client.delete_records(
            name=dataset,
            query="id:10",
            discard_only=False,
            discard_when_forbidden=False,
        )

    matched, processed = argilla_client.delete_records(
        name=dataset,
        query="id:10",
        discard_only=False,
        discard_when_forbidden=True,
    )
    assert matched, processed == (1, 1)


def test_delete_records_with_unmatched_records(mocked_client, api):
    dataset = "test_delete_records_with_unmatched_records"

    api.delete(dataset)
    api.log(
        name=dataset,
        records=[
            argilla.TextClassificationRecord(
                id=i,
                text="This is the text",
                metadata=dict(idx=i),
            )
            for i in range(0, 50)
        ],
    )

    matched, processed = api.delete_records(dataset, ids=["you-wont-find-me-here"])
    assert (matched, processed) == (0, 0)
