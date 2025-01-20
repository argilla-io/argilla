# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Generic, TYPE_CHECKING, TypeVar
from uuid import UUID

from argilla._helpers import LoggingMixin

if TYPE_CHECKING:
    from httpx import Client

__all__ = ["ResourceAPI"]

T = TypeVar("T")


# TODO: Use ABC and align all the abstract method for the different resources APIs
# See comment https://github.com/argilla-io/argilla-python/pull/33#discussion_r1532079989
class ResourceAPI(LoggingMixin, Generic[T]):
    """Base class for all API resources that contains common methods."""

    def __init__(self, http_client: "Client") -> None:
        self.http_client = http_client

    ################
    # CRUD methods #
    ################

    def get(self, id: UUID) -> T:
        raise NotImplementedError

    def create(self, resource: T) -> T:
        raise NotImplementedError

    def delete(self, id: UUID) -> None:
        raise NotImplementedError

    def update(self, resource: T) -> T:
        return resource
