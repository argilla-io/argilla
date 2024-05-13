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

import asyncio
from typing import TYPE_CHECKING, Any, Dict, Optional

import pytest
import pytest_asyncio
from argilla_server.models.base import DatabaseModel
from sqlalchemy import JSON, inspect, select
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column

from tests.pydantic_v1 import BaseModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class Model(DatabaseModel):
    __tablename__ = "model"

    id: Mapped[int] = mapped_column(primary_key=True)
    str_col: Mapped[Optional[str]] = mapped_column()
    int_col: Mapped[Optional[int]] = mapped_column()
    external_id: Mapped[Optional[str]] = mapped_column(unique=True)
    dict_col: Mapped[Optional[Dict[str, Any]]] = mapped_column(MutableDict.as_mutable(JSON))

    __upsertable_columns__ = {"str_col", "int_col"}


class ModelCreateSchema(BaseModel):
    str_col: str
    int_col: int
    external_id: str


@pytest_asyncio.fixture(autouse=True)
async def configure_model_table(connection: "AsyncConnection"):
    await connection.run_sync(Model.__table__.create)

    yield Model

    try:
        await connection.run_sync(Model.__table__.drop)
    except Exception:
        pass


@pytest.mark.asyncio
class TestDatabaseModel:
    async def test_database_model_create(self, db: "AsyncSession"):
        model = await Model.create(db, str_col="unit-test", int_col=1, autocommit=True)
        assert isinstance(model.id, int)
        assert model.id is not None
        assert model.str_col == "unit-test"
        assert model.int_col == 1
        assert model.inserted_at == model.updated_at

    async def test_database_model_create_without_autocommit(self, db: "AsyncSession"):
        model = await Model.create(db, autocommit=False)
        assert inspect(model).pending

    async def test_database_model_read_by(self, db: "AsyncSession"):
        await Model.create(db, str_col="unit-test", int_col=1, autocommit=True)
        model = await Model.read_by(db, str_col="unit-test")
        assert model.id is not None
        assert model.str_col == "unit-test"
        assert model.int_col == 1

    async def test_database_model_read(self, db: "AsyncSession"):
        model = await Model.create(db, str_col="unit-test", int_col=1, autocommit=True)
        model = await Model.read(db, model.id)
        assert model.id is not None
        assert model.str_col == "unit-test"
        assert model.int_col == 1

    async def test_database_model_update(self, db: "AsyncSession"):
        model = await Model.create(
            db, str_col="unit-test", int_col=1, dict_col={"a": 1, "b": 2, "c": 3}, autocommit=True
        )

        model = await model.update(db, str_col="unit-test-2", int_col=2, dict_col={"a": 10}, autocommit=True)
        assert model.str_col == "unit-test-2"
        assert model.int_col == 2
        assert model.dict_col == {"a": 10, "b": 2, "c": 3}

        model = await model.update(
            db, str_col="unit-test-2", int_col=2, dict_col={"a": 10}, replace_dict=True, autocommit=True
        )
        assert model.str_col == "unit-test-2"
        assert model.int_col == 2
        assert model.dict_col == {"a": 10}

    async def test_datbase_model_update_many(self, db: "AsyncSession"):
        model_1 = await Model.create(
            db, str_col="unit-test-1", int_col=1, dict_col={"a": 1, "b": 2, "c": 3}, autocommit=True
        )
        model_2 = await Model.create(
            db, str_col="unit-test-2", int_col=2, dict_col={"a": 4, "b": 5, "c": 6}, autocommit=True
        )
        model_3 = await Model.create(
            db, str_col="unit-test-3", int_col=3, dict_col={"a": 7, "b": 8, "c": 9}, autocommit=True
        )

        await Model.update_many(
            db,
            objects=[
                {"id": model_1.id, "int_col": 4},
                {"id": model_2.id, "int_col": 5},
                {"id": model_3.id, "int_col": 6},
            ],
        )

        assert model_1.int_col == 4
        assert model_2.int_col == 5
        assert model_3.int_col == 6

    async def test_database_model_upsert_many(self, db: "AsyncSession"):
        models = []
        schemas = []
        # These ones will be updated
        for i in range(5):
            models.append(await Model.create(db, str_col=f"unit-test-{i}", int_col=i, external_id=f"external-id-{i}"))
            schemas.append(
                ModelCreateSchema(str_col=f"unit-test-{i}-updated", int_col=i * 10, external_id=f"external-id-{i}")
            )
        # This one has to be inserted
        schemas.append(
            ModelCreateSchema(str_col="unit-test-inserted", int_col=99999, external_id="external-id-inserted")
        )
        models = await Model.upsert_many(db, schemas, constraints=[Model.external_id], autocommit=True)
        for i, model in enumerate(models[:5]):
            assert model.str_col == f"unit-test-{i}-updated"
            assert model.int_col == i * 10
        assert models[-1].str_col == "unit-test-inserted"
        assert models[-1].int_col == 99999

    async def test_database_model_upsert_many_without_objects(self, db: "AsyncSession"):
        with pytest.raises(ValueError, match="Cannot upsert empty list of objects"):
            await Model.upsert_many(db, [], constraints=[Model.external_id], autocommit=True)

    async def test_database_model_upsert(self, db: "AsyncSession"):
        model = await Model.create(db, str_col="unit-test", int_col=1, external_id="12345", autocommit=True)
        await asyncio.sleep(1)
        model = await Model.upsert(
            db,
            ModelCreateSchema(str_col="unit-test-updated", int_col=2, external_id=model.external_id),
            constraints=[Model.external_id],
            autocommit=True,
        )
        assert model.str_col == "unit-test-updated"
        assert model.int_col == 2

    async def test_database_model_upsert_updated_at(self, db: "AsyncSession"):
        model = await Model.create(db, str_col="unit-test", int_col=1, external_id="12345", autocommit=True)
        updated_at = model.updated_at
        await asyncio.sleep(1)

        model = await Model.upsert(
            db,
            ModelCreateSchema(str_col="unit-test-updated", int_col=2, external_id=model.external_id),
            constraints=[Model.external_id],
            autocommit=True,
        )

        assert model.updated_at > updated_at

    async def test_database_model_delete(self, db: "AsyncSession"):
        model = await Model.create(db, str_col="unit-test", int_col=1, autocommit=True)
        model = await model.delete(db)
        assert (await db.execute(select(Model).filter_by(id=model.id))).scalar_one_or_none() is None

    async def test_database_model_delete_many(self, db: "AsyncSession"):
        for i in range(5):
            await Model.create(db, str_col=f"unit-test-{i}", int_col=i, external_id=f"external-id-{i}")
        for i in range(1, 6):
            await Model.create(db, str_col=f"unit-test-{i}", int_col=i * 10, external_id=f"external-id-{i * 10}")

        removed = await Model.delete_many(db, params=[Model.int_col < 10], autocommit=True)

        assert len(removed) == 5
