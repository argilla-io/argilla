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

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Set, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import func, sql
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine.default import DefaultExecutionContext
from sqlalchemy.orm import Mapped, mapped_column
from typing_extensions import Self

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import InstrumentedAttribute
    from sqlalchemy.sql.elements import BinaryExpression

Schema = TypeVar("Schema", bound=BaseModel)

# TODO: remove this once SQLAlchemy has an agnostic insert function
_INSERT_FUNC = {
    "sqlite": sqlite_insert,
    "postgresql": postgres_insert,
    "mysql": mysql_insert,
}


def _schema_or_kwargs(schema: Union[Schema, None], values: Dict[str, Any]) -> Dict[str, Any]:
    if schema:
        return schema.dict()
    return values


class CRUDMixin:
    __upsertable_columns__: Union[Set[str], None] = None

    def fill(self, replace_dict: bool = False, **kwargs: Any) -> Self:
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"Model `{self.__class__.__name__}` has no attribute `{key}`")
            # If the value is a dict, set value for each key one by one, as we want to update only the keys that are in
            # `value` and not override the whole dict.
            if isinstance(value, dict) and not replace_dict:
                dict_col = getattr(self, key) or {}
                dict_col.update(value)
                value = dict_col
            setattr(self, key, value)
        return self

    @classmethod
    async def create(
        cls, db: "AsyncSession", schema: Union[Schema, None] = None, autocommit: bool = True, **kwargs: Any
    ) -> Self:
        _values = _schema_or_kwargs(schema, kwargs)
        instance = cls()
        instance.fill(**_values)
        return await instance.save(db, autocommit)

    @classmethod
    async def read(cls, db: "AsyncSession", id: Any, key: str = "id") -> Union[Self, None]:
        params = {key: id}
        return await cls.read_by(db, **params)

    @classmethod
    async def read_by(cls, db: "AsyncSession", **params: Any) -> Union[Self, None]:
        query = sql.select(cls).filter_by(**params)
        result = await db.execute(query)
        return result.scalars().unique().one_or_none()

    async def update(
        self,
        db: "AsyncSession",
        schema: Union[Schema, None] = None,
        replace_dict: bool = False,
        autocommit: bool = True,
        **kwargs: Any,
    ) -> Self:
        _values = _schema_or_kwargs(schema, kwargs)
        updated = self.fill(replace_dict=replace_dict, **_values)
        return await updated.save(db, autocommit)

    @classmethod
    async def upsert_many(
        cls,
        db: "AsyncSession",
        objects: List[Schema],
        constraints: List["InstrumentedAttribute[Any]"],
        autocommit: bool = True,
    ) -> List[Self]:
        if len(objects) == 0:
            raise ValueError("Cannot upsert empty list of objects")
        values = [obj.dict() for obj in objects]

        # Try to insert all objects
        insert_stmt = _INSERT_FUNC[db.bind.dialect.name](cls).values(values)

        # On conflict, update the columns that are upsertable (defined in `Model.__upsertable_columns__`)
        columns_to_update = {column: getattr(insert_stmt.excluded, column) for column in cls.__upsertable_columns__}
        # onupdate for `updated_at` is not working. We need to force a new value on update
        if hasattr(cls, "updated_at"):
            columns_to_update["updated_at"] = datetime.utcnow()
        upsert_stmt = (
            insert_stmt.on_conflict_do_update(index_elements=constraints, set_=columns_to_update)
            .returning(cls)
            .execution_options(populate_existing=True)
        )

        result = await db.execute(upsert_stmt)
        if autocommit:
            await db.commit()

        return result.scalars().all()

    @classmethod
    async def upsert(
        cls,
        db: "AsyncSession",
        schema: Schema,
        constraints: List["InstrumentedAttribute[Any]"],
        autocommit: bool = True,
    ) -> Self:
        upserted = await cls.upsert_many(db, [schema], constraints, autocommit)
        return upserted[0]

    async def delete(self, db: "AsyncSession", autocommit: bool = True) -> Self:
        await db.delete(self)
        if autocommit:
            await db.commit()
        return self

    @classmethod
    async def delete_many(
        cls, db: "AsyncSession", params: List["BinaryExpression"], autocommit: bool = True
    ) -> List[Self]:
        delete_stmt = sql.delete(cls).filter(*params).returning(cls)
        result = await db.execute(delete_stmt)
        if autocommit:
            await db.commit()
        return result.scalars().all()

    async def save(self, db: "AsyncSession", autocommit: bool = True) -> Self:
        db.add(self)
        if autocommit:
            await db.commit()
        return self


def _default_inserted_at(context: DefaultExecutionContext) -> datetime:
    return context.get_current_parameters(isolate_multiinsert_groups=False)["inserted_at"]


class TimestampMixin:
    inserted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=_default_inserted_at, onupdate=datetime.utcnow)
