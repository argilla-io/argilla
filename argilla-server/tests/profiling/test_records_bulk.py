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

from typing import Union

import argilla_server.apis.v1.handlers.datasets.records_bulk
import pytest
from argilla_server.contexts import datasets
from argilla_server.models import Dataset, Question, VectorSettings
from argilla_server.schemas.v1.records import RecordCreate, RecordsCreate
from argilla_server.schemas.v1.records_bulk import RecordsBulkCreate
from argilla_server.schemas.v1.responses import UserDraftResponseCreate
from argilla_server.schemas.v1.suggestions import SuggestionCreate
from argilla_server.search_engine import ElasticSearchEngine
from pyinstrument import Profiler
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory
from tests.unit.api.v1.datasets.records.records_bulk.test_dataset_records_bulk import TestDatasetRecordsBulk


def _get_dataset_question_by_name(dataset: Dataset, name: str) -> Union["Question", None]:
    for question in dataset.questions:
        if question.name == name:
            return question


def _get_dataset_vector_settings_by_name(dataset: Dataset, name: str) -> Union["VectorSettings", None]:
    for vector_settings in dataset.vectors_settings:
        if vector_settings.name == name:
            return vector_settings


@pytest.mark.asyncio
class TestUpsertRecordsBulk:
    async def test_profiling_for_create_records(self, db: AsyncSession, elasticsearch_config: dict):
        engine = ElasticSearchEngine(config=elasticsearch_config, number_of_replicas=0, number_of_shards=1)
        dataset = await TestDatasetRecordsBulk().test_dataset()

        users = await UserFactory.create_batch(3)

        comments = _get_dataset_question_by_name(dataset, "comments")
        rating = _get_dataset_question_by_name(dataset, "rating")

        vector_settings = _get_dataset_vector_settings_by_name(dataset, "medium")

        sample_record = RecordCreate(
            fields={
                "prompt": "Does exercise help reduce stress?",
                "response": "Exercise can definitely help reduce stress.",
            },
            metadata={"terms_metadata": ["a", "b", "c"]},
            suggestions=[
                SuggestionCreate(question_id=comments.id, value="The comments"),
                SuggestionCreate(question_id=rating.id, value=3),
            ],
            responses=[
                UserDraftResponseCreate(
                    user_id=user.id,
                    values={
                        "comments": {"value": "Response comments"},
                        "rating": {"value": 4},
                    },
                    status="draft",
                )
                for user in users
            ],
            vectors={vector_settings.name: [1.5] * vector_settings.dimensions},
        )

        records_create = RecordsCreate(items=[sample_record] * 1000)

        profiler = Profiler()
        with profiler:
            await argilla_server.apis.v1.handlers.datasets.records_bulk.create_dataset_records_bulk(
                dataset, records_create
            )
        profiler.open_in_browser()

        profiler.reset()
        with profiler:
            await datasets.create_records(db, engine, dataset, records_create)
        profiler.open_in_browser()

    async def test_profiling_for_create_records_bulk(self, db: AsyncSession, elasticsearch_config: dict):
        engine = ElasticSearchEngine(config=elasticsearch_config, number_of_replicas=0, number_of_shards=1)
        dataset = await TestDatasetRecordsBulk().test_dataset()

        users = await UserFactory.create_batch(3)

        comments = _get_dataset_question_by_name(dataset, "comments")
        rating = _get_dataset_question_by_name(dataset, "rating")

        vector_settings = _get_dataset_vector_settings_by_name(dataset, "medium")

        sample_record = RecordCreate(
            fields={
                "prompt": "Does exercise help reduce stress?",
                "response": "Exercise can definitely help reduce stress.",
            },
            metadata={"terms_metadata": ["a", "b", "c"]},
            suggestions=[
                SuggestionCreate(question_id=comments.id, value="The comments"),
                SuggestionCreate(question_id=rating.id, value=3),
            ],
            responses=[
                UserDraftResponseCreate(
                    user_id=user.id,
                    values={
                        "comments": {"value": "Response comments"},
                        "rating": {"value": 4},
                    },
                    status="draft",
                )
                for user in users
            ],
            vectors={vector_settings.name: [1.5] * vector_settings.dimensions},
        )
        records_upsert = RecordsBulkCreate(items=[sample_record] * 1000)

        profiler = Profiler()
        with profiler:
            await CreateRecordsBulk(db, engine).create_records_bulk(dataset, records_upsert)
        profiler.open_in_browser()
