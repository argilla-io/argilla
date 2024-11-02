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
from abc import abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from argilla._exceptions import ArgillaSerializeError
from argilla._helpers import LoggingMixin

if TYPE_CHECKING:
    from argilla._api._base import ResourceAPI
    from argilla._models import ResourceModel
    from argilla.client import Argilla


class Resource(LoggingMixin):
    """Base class for all resources (Dataset, Workspace, User, etc.)"""

    _model: "ResourceModel"
    _client: "Argilla"
    _api: "ResourceAPI"

    _MAX_OUTDATED_RETENTION = 30

    def __init__(self, api: Optional["ResourceAPI"] = None, client: Optional["Argilla"] = None) -> None:
        self._client = client
        self._api = api

        self._last_api_call = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._model})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Resource):
            return False
        if not hasattr(other, "_model"):
            return super().__eq__(other)
        return self._model == other._model

    @property
    def id(self) -> Optional[UUID]:
        return self._model.id

    @id.setter
    def id(self, value: UUID) -> None:
        self._model.id = value

    @property
    def inserted_at(self) -> datetime:
        return self._model.inserted_at

    @property
    def updated_at(self) -> datetime:
        return self._model.updated_at

    @property
    def is_outdated(self) -> bool:
        """Checks if the resource is outdated based on the last API call
        Returns:
            bool: True if the resource is outdated, False otherwise
        """
        seconds = self._seconds_from_last_api_call()
        if seconds is None:
            return True
        return seconds > self._MAX_OUTDATED_RETENTION

    def api_model(self):
        """Returns the model that is used to interact with the API"""
        return self._model

    ############################
    # CRUD operations
    ############################

    def create(self) -> "Resource":
        response_model = self._api.create(self.api_model())
        self._model = response_model
        self._update_last_api_call()
        self._log_message(f"Resource created: {self}")
        return self

    def get(self) -> "Resource":
        response_model = self._api.get(self.api_model().id)
        self._model = response_model
        self._update_last_api_call()
        self._log_message(f"Resource fetched: {self}")
        return self

    def update(self) -> "Resource":
        response_model = self._api.update(self.api_model())
        self._model = response_model
        self._update_last_api_call()
        self._log_message(f"Resource updated: {self}")
        return self

    def delete(self) -> None:
        self._api.delete(self.api_model().id)
        self._update_last_api_call()
        self._log_message(f"Resource deleted: {self}")

    ############################
    # Serialization
    ############################

    def serialize(self) -> dict[str, Any]:
        try:
            return self.api_model().model_dump()
        except Exception as e:
            raise ArgillaSerializeError(f"Failed to serialize the resource. {e.__class__.__name__}") from e

    def serialize_json(self) -> str:
        try:
            return self.api_model().model_dump_json()
        except Exception as e:
            raise ArgillaSerializeError(f"Failed to serialize the resource. {e.__class__.__name__}") from e

    def _update_last_api_call(self):
        self._last_api_call = datetime.utcnow()

    def _seconds_from_last_api_call(self) -> Optional[float]:
        if self._last_api_call:
            return (datetime.utcnow() - self._last_api_call).total_seconds()

    @abstractmethod
    def _with_client(self, client: "Argilla") -> "Self":
        pass
