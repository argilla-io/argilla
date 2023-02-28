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
from argilla.client.sdk.commons.errors import ForbiddenApiError


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


def test_delete_records_without_permission(mocked_client):
    dataset = "test_delete_records_without_permission"
    import argilla as rg

    rg.delete(dataset)
    rg.log(
        name=dataset,
        records=[
            rg.TextClassificationRecord(id=i, text="This is the text", metadata=dict(idx=i)) for i in range(0, 50)
        ],
    )
    try:
        mocked_client.change_current_user("mock-user")
        matched, processed = rg.delete_records(
            name=dataset,
            ids=[10],
            discard_only=True,
        )
        assert matched, processed == (1, 1)

        with pytest.raises(ForbiddenApiError):
            rg.delete_records(
                name=dataset,
                query="id:10",
                discard_only=False,
                discard_when_forbidden=False,
            )

        matched, processed = rg.delete_records(
            name=dataset,
            query="id:10",
            discard_only=False,
            discard_when_forbidden=True,
        )
        assert matched, processed == (1, 1)
    finally:
        mocked_client.reset_default_user()


def test_delete_records_with_unmatched_records(mocked_client):
    dataset = "test_delete_records_with_unmatched_records"
    import argilla as rg

    rg.delete(dataset)
    rg.log(
        name=dataset,
        records=[
            rg.TextClassificationRecord(
                id=i,
                text="This is the text",
                metadata=dict(idx=i),
            )
            for i in range(0, 50)
        ],
    )

    matched, processed = rg.delete_records(dataset, ids=["you-wont-find-me-here"])
    assert (matched, processed) == (0, 0)
