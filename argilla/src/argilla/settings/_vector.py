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

from typing import Optional, TYPE_CHECKING

from argilla._api._vectors import VectorsAPI
from argilla._models import VectorFieldModel
from argilla._resource import Resource
from argilla.client import Argilla

if TYPE_CHECKING:
    from argilla import Dataset

__all__ = ["VectorField"]


class VectorField(Resource):
    """Vector field for use in Argilla `Dataset` `Settings`"""

    _model: VectorFieldModel
    _api: VectorsAPI
    _dataset: Optional["Dataset"]

    def __init__(
        self,
        name: str,
        dimensions: int,
        title: Optional[str] = None,
        _client: Optional["Argilla"] = None,
    ) -> None:
        """Vector field for use in Argilla `Dataset` `Settings`

        Parameters:
            name (str): The name of the vector field
            dimensions (int): The number of dimensions in the vector
            title (Optional[str]): The title of the vector to be shown in the UI.
        """
        client = _client or Argilla._get_default()
        super().__init__(api=client.api.vectors, client=client)
        self._model = VectorFieldModel(name=name, title=title, dimensions=dimensions)
        self._dataset = None

    @property
    def name(self) -> str:
        return self._model.name

    @name.setter
    def name(self, value: str) -> None:
        self._model.name = value

    @property
    def title(self) -> Optional[str]:
        return self._model.title

    @title.setter
    def title(self, value: Optional[str]) -> None:
        self._model.title = value

    @property
    def dimensions(self) -> int:
        return self._model.dimensions

    @dimensions.setter
    def dimensions(self, value: int) -> None:
        self._model.dimensions = value

    @property
    def dataset(self) -> "Dataset":
        return self._dataset

    @dataset.setter
    def dataset(self, value: "Dataset") -> None:
        self._dataset = value
        self._model.dataset_id = self._dataset.id
        self._with_client(self._dataset._client)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, title={self.title}, dimensions={self.dimensions})"

    @classmethod
    def from_model(cls, model: VectorFieldModel) -> "VectorField":
        instance = cls(name=model.name, dimensions=model.dimensions)
        instance._model = model

        return instance

    @classmethod
    def from_dict(cls, data: dict) -> "VectorField":
        model = VectorFieldModel(**data)
        return cls.from_model(model=model)

    def _with_client(self, client: "Argilla") -> "VectorField":
        # TODO: Review and simplify. Maybe only one of them is required
        self._client = client
        self._api = self._client.api.vectors

        return self
