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

from abc import ABC, abstractmethod
from typing import Optional, Type
from uuid import UUID

import httpx
from pydantic import BaseModel


class RemoteSchema(BaseModel, ABC):
    id: Optional[UUID] = None
    client: Optional[httpx.Client] = None

    # TODO(alvarobartt): here to be able to use the `allowed_for_roles` decorator
    @property
    def _client(self) -> Optional[httpx.Client]:
        return self.client

    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True

    @abstractmethod
    def to_local(self) -> BaseModel:
        """Abstract method to be implemented by subclasses to convert the remote schema
        to a local one.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_api(cls, payload: "BaseModel") -> Type["RemoteSchema"]:
        """Abstract method to be implemented by subclasses to convert the API payload
        into a remote schema."""
        raise NotImplementedError
