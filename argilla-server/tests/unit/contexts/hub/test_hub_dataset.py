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

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.api.schemas.v1.datasets import HubDatasetMapping, HubDatasetMappingItem
from argilla_server.api.schemas.v1.metadata_properties import IntegerMetadataProperty
from argilla_server.enums import DatasetStatus, QuestionType
from argilla_server.models import Record
from argilla_server.contexts.hub import HubDataset
from argilla_server.search_engine import SearchEngine

from tests.factories import (
    DatasetFactory,
    ImageFieldFactory,
    RatingQuestionFactory,
    TextFieldFactory,
    IntegerMetadataPropertyFactory,
)


@pytest.mark.asyncio
class TestHubDataset:
    async def test_hub_dataset_import_to(self, db: AsyncSession, mock_search_engine: SearchEngine):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await TextFieldFactory.create(name="package_name", required=True, dataset=dataset)
        await TextFieldFactory.create(name="review", required=True, dataset=dataset)
        await TextFieldFactory.create(name="date", dataset=dataset)
        await TextFieldFactory.create(name="star", dataset=dataset)

        await IntegerMetadataPropertyFactory.create(name="version_id", dataset=dataset)

        await dataset.awaitable_attrs.fields
        await dataset.awaitable_attrs.questions
        await dataset.awaitable_attrs.metadata_properties

        hub_dataset = HubDataset(
            name="lhoestq/demo1",
            subset="default",
            split="train",
            mapping=HubDatasetMapping(
                fields=[
                    HubDatasetMappingItem(source="package_name", target="package_name"),
                    HubDatasetMappingItem(source="review", target="review"),
                    HubDatasetMappingItem(source="date", target="date"),
                    HubDatasetMappingItem(source="star", target="star"),
                ],
                metadata=[
                    HubDatasetMappingItem(source="version_id", target="version_id"),
                ],
                external_id="id",
            ),
        )

        await hub_dataset.take(1).import_to(db, mock_search_engine, dataset)

        record = (await db.execute(select(Record))).scalar_one()
        assert record.external_id == "7bd227d9-afc9-11e6-aba1-c4b301cdf627"
        assert record.fields["package_name"] == "com.mantz_it.rfanalyzer"
        assert (
            record.fields["review"]
            == "Great app! The new version now works on my Bravia Android TV which is great as it's right by my rooftop aerial cable. The scan feature would be useful...any ETA on when this will be available? Also the option to import a list of bookmarks e.g. from a simple properties file would be useful."
        )
        assert record.fields["date"] == "October 12 2016"
        assert record.fields["star"] == "4"
        assert record.metadata_ == {"version_id": 1487}

    async def test_hub_dataset_import_to_with_suggestions(self, db: AsyncSession, mock_search_engine: SearchEngine):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await TextFieldFactory.create(name="package_name", required=True, dataset=dataset)
        await TextFieldFactory.create(name="review", required=True, dataset=dataset)

        question = await RatingQuestionFactory.create(
            name="star",
            required=True,
            dataset=dataset,
            settings={
                "type": QuestionType.rating,
                "options": [
                    {"value": 1},
                    {"value": 2},
                    {"value": 3},
                    {"value": 4},
                    {"value": 5},
                ],
            },
        )

        await dataset.awaitable_attrs.fields
        await dataset.awaitable_attrs.questions
        await dataset.awaitable_attrs.metadata_properties

        hub_dataset = HubDataset(
            name="lhoestq/demo1",
            subset="default",
            split="train",
            mapping=HubDatasetMapping(
                fields=[
                    HubDatasetMappingItem(source="package_name", target="package_name"),
                    HubDatasetMappingItem(source="review", target="review"),
                ],
                suggestions=[
                    HubDatasetMappingItem(source="star", target="star"),
                ],
            ),
        )

        await hub_dataset.take(1).import_to(db, mock_search_engine, dataset)

        record = (await db.execute(select(Record))).scalar_one()
        assert record.suggestions[0].value == 4
        assert record.suggestions[0].question_id == question.id

    async def test_hub_dataset_import_to_with_image_fields(self, db: AsyncSession, mock_search_engine: SearchEngine):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ImageFieldFactory.create(name="image-to-review", required=True, dataset=dataset)

        await dataset.awaitable_attrs.fields
        await dataset.awaitable_attrs.questions
        await dataset.awaitable_attrs.metadata_properties

        hub_dataset = HubDataset(
            name="lmms-lab/llava-critic-113k",
            subset="pairwise",
            split="train",
            mapping=HubDatasetMapping(
                fields=[
                    HubDatasetMappingItem(source="image", target="image-to-review"),
                ],
                external_id="id",
            ),
        )

        await hub_dataset.take(1).import_to(db, mock_search_engine, dataset)

        record = (await db.execute(select(Record))).scalar_one()
        assert record.external_id == "vlfeedback_1"
        assert (
            record.fields["image-to-review"][:100]
            == "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aH"
        )

    async def test_hub_dataset_import_to_idempotency_with_external_id(
        self, db: AsyncSession, mock_search_engine: SearchEngine
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await TextFieldFactory.create(name="package_name", required=True, dataset=dataset)

        await dataset.awaitable_attrs.fields
        await dataset.awaitable_attrs.questions
        await dataset.awaitable_attrs.metadata_properties

        hub_dataset = HubDataset(
            name="lhoestq/demo1",
            subset="default",
            split="train",
            mapping=HubDatasetMapping(
                fields=[
                    HubDatasetMappingItem(source="package_name", target="package_name"),
                ],
                external_id="id",
            ),
        )

        await hub_dataset.import_to(db, mock_search_engine, dataset)
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 5

        await hub_dataset.import_to(db, mock_search_engine, dataset)
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 5

        records = (await db.execute(select(Record))).scalars().all()
        assert [record.external_id for record in records] == [
            "7bd227d9-afc9-11e6-aba1-c4b301cdf627",
            "7bd22905-afc9-11e6-a5dc-c4b301cdf627",
            "7bd2299c-afc9-11e6-85d6-c4b301cdf627",
            "7bd22a26-afc9-11e6-9309-c4b301cdf627",
            "7bd22aba-afc9-11e6-8293-c4b301cdf627",
        ]

    async def test_hub_dataset_import_to_idempotency_without_external_id(
        self, db: AsyncSession, mock_search_engine: SearchEngine
    ):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await TextFieldFactory.create(name="package_name", required=True, dataset=dataset)

        await dataset.awaitable_attrs.fields
        await dataset.awaitable_attrs.questions
        await dataset.awaitable_attrs.metadata_properties

        hub_dataset = HubDataset(
            name="lhoestq/demo1",
            subset="default",
            split="train",
            mapping=HubDatasetMapping(
                fields=[
                    HubDatasetMappingItem(source="package_name", target="package_name"),
                ],
            ),
        )

        await hub_dataset.import_to(db, mock_search_engine, dataset)
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 5

        await hub_dataset.import_to(db, mock_search_engine, dataset)
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 5

        records = (await db.execute(select(Record))).scalars().all()
        assert [record.external_id for record in records] == ["0", "1", "2", "3", "4"]

    async def test_hub_dataset_num_rows(self):
        hub_dataset = HubDataset(
            name="lhoestq/demo1",
            subset="default",
            split="train",
            mapping=HubDatasetMapping(
                fields=[
                    HubDatasetMappingItem(source="package_name", target="package_name"),
                ],
                metadata=[],
                suggestions=[],
                external_id=None,
            ),
        )

        assert hub_dataset.num_rows == 5
