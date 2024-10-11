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

from argilla_server.api.schemas.v1.metadata_properties import IntegerMetadataProperty
from argilla_server.enums import DatasetStatus
from argilla_server.models import Record
from argilla_server.contexts.hub import HubDataset
from argilla_server.search_engine import SearchEngine

from tests.factories import DatasetFactory, ImageFieldFactory, TextFieldFactory, IntegerMetadataPropertyFactory


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
        await dataset.awaitable_attrs.metadata_properties

        hub_dataset = HubDataset(name="lhoestq/demo1", subset="default", split="train")

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

    async def test_hub_dataset_import_to_idempotency(self, db: AsyncSession, mock_search_engine: SearchEngine):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await TextFieldFactory.create(name="package_name", required=True, dataset=dataset)

        await dataset.awaitable_attrs.fields
        await dataset.awaitable_attrs.metadata_properties

        hub_dataset = HubDataset(name="lhoestq/demo1", subset="default", split="train")

        await hub_dataset.import_to(db, mock_search_engine, dataset)
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 5

        await hub_dataset.import_to(db, mock_search_engine, dataset)
        assert (await db.execute(select(func.count(Record.id)))).scalar_one() == 5

    async def test_hub_dataset_import_image_fields(self, db: AsyncSession, mock_search_engine: SearchEngine):
        dataset = await DatasetFactory.create(status=DatasetStatus.ready)

        await ImageFieldFactory.create(name="image", required=True, dataset=dataset)

        await dataset.awaitable_attrs.fields
        await dataset.awaitable_attrs.metadata_properties

        hub_dataset = HubDataset(name="lmms-lab/llava-critic-113k", subset="pairwise", split="train")

        await hub_dataset.take(1).import_to(db, mock_search_engine, dataset)

        record = (await db.execute(select(Record))).scalar_one()
        assert record.external_id == "vlfeedback_1"
        assert (
            record.fields["image"][:100]
            == "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aH"
        )

    async def test_hub_dataset_num_rows(self):
        hub_dataset = HubDataset(name="lhoestq/demo1", subset="default", split="train")

        assert hub_dataset.num_rows == 5
