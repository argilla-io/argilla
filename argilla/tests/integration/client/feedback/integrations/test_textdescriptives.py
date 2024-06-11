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

import pytest
from argilla_v1 import init
from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla_v1.client.feedback.integrations.textdescriptives import TextDescriptivesExtractor
from argilla_v1.client.feedback.schemas.fields import TextField
from argilla_v1.client.feedback.schemas.questions import TextQuestion
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from typing_extensions import TYPE_CHECKING

from tests.factories import WorkspaceFactory

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop

    from argilla_v1 import User


@pytest.fixture(scope="function")
def records() -> List[FeedbackRecord]:
    return [
        FeedbackRecord(fields={"field_1": "This is a test", "field_2": "This is a test"}),
        FeedbackRecord(
            fields={
                "field_1": "This is a test",
            }
        ),
        FeedbackRecord(
            fields={"field_1": "This is a test", "field_2": "This is a test"},
        ),
    ]


@pytest.fixture(scope="function")
def dataset() -> FeedbackDataset:
    ds = FeedbackDataset(
        fields=[
            TextField(name="field_1"),
            TextField(name="field_2", required=False),
        ],
        questions=[
            TextQuestion(name="question_1"),
        ],
    )
    return ds


@pytest.fixture(scope="session")
def td_extractor() -> TextDescriptivesExtractor:
    return TextDescriptivesExtractor()


@pytest.mark.usefixtures("td_extractor", "records")
def test_update_records(td_extractor: TextDescriptivesExtractor, records: List[FeedbackRecord]) -> None:
    records = td_extractor.update_records(records, fields=["field_1"])
    assert "field_1_n_tokens" in records[0].metadata
    assert "field_2_n_tokens" not in records[0].metadata
    records = td_extractor.update_records(records, fields=["field_2"])
    assert "field_1_n_tokens" in records[0].metadata
    assert "field_2_n_tokens" in records[0].metadata


@pytest.mark.asyncio(scope="function")
@pytest.mark.usefixtures("owner", "td_extractor", "dataset", "records")
@pytest.mark.parametrize("remote", [True, False])
async def test_update_dataset(
    remote: bool,
    td_extractor: TextDescriptivesExtractor,
    dataset: FeedbackDataset,
    records: List[FeedbackRecord],
    owner: "User",
    event_loop: "AbstractEventLoop",
) -> None:
    dataset.add_records(records)
    if remote:
        init(api_key=owner.api_key)
        ws_name, ds_name = "test_workspace", "td_extractor_test"
        ws = await WorkspaceFactory.create(name=ws_name)
        dataset = dataset.push_to_argilla(name=ds_name, workspace=ws.name)
        dataset = FeedbackDataset.from_argilla(name=ds_name, workspace=ws.name)
    dataset = td_extractor.update_dataset(dataset, fields=["field_1"], update_records=False)
    assert dataset.metadata_property_by_name("field_1_n_tokens")
    assert not dataset.metadata_property_by_name("field_2_n_tokens")
    assert not dataset.records[0].metadata
    dataset = td_extractor.update_dataset(dataset, fields=["field_2"], update_records=False)
    dataset = td_extractor.update_dataset(dataset, update_records=True, fields=["field_1"])
    assert "field_1_n_tokens" in dataset.records[0].metadata
    assert "field_2_n_tokens" not in dataset.records[0].metadata
    dataset = td_extractor.update_dataset(dataset, update_records=True, fields=["field_2"])
    assert "field_1_n_tokens" in dataset.records[0].metadata
    assert "field_2_n_tokens" in dataset.records[0].metadata
    assert "field_2_n_tokens" not in dataset.records[1].vectors
