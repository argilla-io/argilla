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

import pytest
from argilla_server.models import User, UserRole
from argilla_v1.client.api import delete_records, load, log
from argilla_v1.client.client import Argilla
from argilla_v1.client.models import TextClassificationRecord
from argilla_v1.client.sdk.commons.errors import ForbiddenApiError
from argilla_v1.client.singleton import init

from tests.factories import AnnotatorFactory, UserFactory, WorkspaceFactory
from tests.integration.utils import delete_ignoring_errors


def test_delete_records_from_dataset(argilla_user: "User"):
    dataset = "test_delete_records_from_dataset"

    init(api_key=argilla_user.api_key, workspace=argilla_user.username)
    delete_ignoring_errors(dataset)
    log(
        name=dataset,
        records=[TextClassificationRecord(id=i, text="This is the text", metadata=dict(idx=i)) for i in range(0, 50)],
    )

    matched, processed = delete_records(name=dataset, ids=[10], discard_only=True)
    assert matched, processed == (1, 1)

    ds = load(name=dataset)
    assert len(ds) == 50

    time.sleep(1)
    matched, processed = delete_records(name=dataset, query="id:10", discard_only=False)
    assert matched, processed == (1, 1)

    time.sleep(1)
    ds = load(name=dataset)
    assert len(ds) == 49


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.asyncio
async def test_delete_records_without_permission(owner: User, role: UserRole):
    dataset = "test_delete_records_without_permission"

    workspace = await WorkspaceFactory.create()

    client = Argilla(api_key=owner.api_key, workspace=workspace.name)

    delete_ignoring_errors(dataset)
    records = [TextClassificationRecord(id=i, text="This is the text", metadata=dict(idx=i)) for i in range(0, 50)]
    client.log(name=dataset, records=records)

    user = await UserFactory.create(role=role, workspaces=[workspace])
    client = Argilla(api_key=user.api_key, workspace=workspace.name)

    matched, processed = client.delete_records(name=dataset, ids=[10], discard_only=True)
    assert matched, processed == (1, 1)

    annotator = await AnnotatorFactory.create(workspaces=[workspace])

    client = Argilla(api_key=annotator.api_key, workspace=workspace.name)
    with pytest.raises(ForbiddenApiError):
        client.delete_records(name=dataset, query="id:11", discard_only=False, discard_when_forbidden=False)

    matched, processed = client.delete_records(
        name=dataset, query="id:11", discard_only=False, discard_when_forbidden=True
    )
    assert matched, processed == (1, 1)


def test_delete_records_with_unmatched_records(api):
    dataset = "test_delete_records_with_unmatched_records"

    delete_ignoring_errors(dataset)
    api.log(
        name=dataset,
        records=[TextClassificationRecord(id=i, text="This is the text", metadata=dict(idx=i)) for i in range(0, 50)],
    )

    matched, processed = api.delete_records(dataset, ids=["you-wont-find-me-here"])
    assert (matched, processed) == (0, 0)
