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

import argilla_v1.client.singleton as rg
import pytest
from argilla_v1 import User, ValueSchema, Workspace
from argilla_v1.client.feedback.schemas.enums import ResponseStatus
from argilla_v1.client.sdk.users.models import UserRole
from argilla_v1.feedback import FeedbackDataset, FeedbackRecord, ResponseSchema, TextField, TextQuestion


class TestListDatasetRecords:
    @pytest.mark.parametrize("offset", [0, 20, 30, 50, 60, 80, 90])
    @pytest.mark.parametrize("limit", [20, 40, 50, 60, 80, 90, 150])
    def test_list_dataset_records_with_multiple_responses_and_variable_offset(
        self, owner: User, offset: int, limit: int
    ):
        rg.init(api_key=owner.api_key)

        ws = Workspace.create(name="test-workspace")

        annotator, other_annotator = (
            User.create(
                username="annotator",
                password="password",
                role=UserRole.annotator,
                workspaces=[ws.name],
            ),
            User.create(
                username="other-annotator",
                password="password",
                role=UserRole.annotator,
                workspaces=[ws.name],
            ),
        )

        dataset = FeedbackDataset(fields=[TextField(name="text")], questions=[TextQuestion(name="question")])

        records = [
            FeedbackRecord(
                external_id=f"seq-{i}",
                fields={"text": "Hello world!"},
                responses=[
                    ResponseSchema(user_id=annotator.id, values={"question": ValueSchema(value="Hello world!")}),
                    ResponseSchema(user_id=other_annotator.id, values={}, status=ResponseStatus.discarded),
                ],
            )
            for i in range(0, 100)
        ]
        dataset.add_records(records)

        remote = dataset.push_to_argilla(name="test_dataset", workspace=ws)
        assert len(remote) == len(records)

        chunk_remote = remote[offset : offset + limit]
        chunk_records = records[offset : offset + limit]

        for i, record in enumerate(chunk_records):
            assert record.external_id == chunk_remote[i].external_id
