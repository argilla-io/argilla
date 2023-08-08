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

from typing import TYPE_CHECKING

import pytest
from argilla.client import api
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.schemas.records import FeedbackRecord, RemoteFeedbackRecord, SuggestionSchema
from argilla.client.sdk.users.models import UserRole

from tests.factories import DatasetFactory, RecordFactory, TextFieldFactory, TextQuestionFactory, UserFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.asyncio
async def test_delete(role: UserRole) -> None:
    text_field = await TextFieldFactory.create(required=True)
    text_question = await TextQuestionFactory.create(required=True)
    records = await RecordFactory.create_batch(size=10)
    dataset = await DatasetFactory.create(
        fields=[text_field],
        questions=[text_question],
        records=records,
    )
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api.init(api_key=user.api_key)
    remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
    remote_records = [record for record in remote_dataset.records]
    assert all(isinstance(record, RemoteFeedbackRecord) for record in remote_records)

    deleted_records = []
    for record in remote_records:
        deleted_records.append(record.delete())
    assert all(isinstance(record, FeedbackRecord) for record in deleted_records)
    assert len(remote_dataset.records) == 0


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.asyncio
async def test_update(role: UserRole, db: "AsyncSession") -> None:
    text_field = await TextFieldFactory.create(required=True)
    text_question = await TextQuestionFactory.create(required=True)
    records = await RecordFactory.create_batch(size=10)
    dataset = await DatasetFactory.create(
        fields=[text_field],
        questions=[text_question],
        records=records,
    )
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api.init(api_key=user.api_key)
    remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
    remote_records = [record for record in remote_dataset.records]
    assert all(isinstance(record, RemoteFeedbackRecord) for record in remote_records)
    assert all(record.suggestions == () for record in remote_records)

    suggestion = SuggestionSchema(
        question_id=text_question.id,
        question_name=text_question.name,
        value="suggestion",
    )
    for remote_record, factory_record in zip(remote_records, records):
        remote_record.update(suggestions=[suggestion])
        await db.refresh(factory_record, attribute_names=["suggestions"])
    assert all(record.suggestions == (suggestion,) for record in remote_dataset.records)


@pytest.mark.parametrize("role", [UserRole.owner, UserRole.admin])
@pytest.mark.asyncio
async def test_set_suggestions_deprecated(role: UserRole, db: "AsyncSession") -> None:
    text_field = await TextFieldFactory.create(required=True)
    text_question = await TextQuestionFactory.create(required=True)
    records = await RecordFactory.create_batch(size=10)
    dataset = await DatasetFactory.create(
        fields=[text_field],
        questions=[text_question],
        records=records,
    )
    user = await UserFactory.create(role=role, workspaces=[dataset.workspace])

    api.init(api_key=user.api_key)
    remote_dataset = FeedbackDataset.from_argilla(id=dataset.id)
    remote_records = [record for record in remote_dataset.records]
    assert all(isinstance(record, RemoteFeedbackRecord) for record in remote_records)
    assert all(record.suggestions == () for record in remote_records)

    suggestion = SuggestionSchema(
        question_id=text_question.id,
        question_name=text_question.name,
        value="suggestion",
    )
    with pytest.warns(DeprecationWarning, match="`set_suggestions` is deprected in favor of `update`"):
        for remote_record, factory_record in zip(remote_records, records):
            remote_record.set_suggestions(suggestions=[suggestion])
            await db.refresh(factory_record, attribute_names=["suggestions"])
    assert all(record.suggestions == (suggestion,) for record in remote_dataset.records)
