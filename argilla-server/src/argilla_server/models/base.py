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
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncAttrs, async_object_session, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from argilla_server.models.mixins import CRUDMixin, TimestampMixin


class DatabaseModel(DeclarativeBase, AsyncAttrs, CRUDMixin, TimestampMixin):
    __abstract__ = True

    # Required in order to access columns with server defaults or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    def is_relationship_loaded(self, relationship: str) -> bool:
        return relationship in self.__dict__

    @property
    def current_async_session(self) -> Optional[AsyncSession]:
        return async_object_session(self)
