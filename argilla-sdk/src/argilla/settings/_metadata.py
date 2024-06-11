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

from typing import Optional, Union, List, TYPE_CHECKING

from argilla._api._metadata import MetadataAPI
from argilla._exceptions import MetadataError
from argilla._models import (
    MetadataPropertyType,
    TermsMetadataPropertySettings,
    FloatMetadataPropertySettings,
    IntegerMetadataPropertySettings,
    MetadataFieldModel,
)
from argilla._resource import Resource
from argilla.client import Argilla

if TYPE_CHECKING:
    from argilla import Dataset

__all__ = [
    "TermsMetadataProperty",
    "FloatMetadataProperty",
    "IntegerMetadataProperty",
    "MetadataType",
]


class MetadataPropertyBase(Resource):
    _model: MetadataFieldModel
    _api: MetadataAPI

    _dataset: "Dataset"

    def __init__(self, client: Optional[Argilla] = None) -> None:
        client = client or Argilla._get_default()
        super().__init__(client=client, api=client.api.metadata)

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
    def visible_for_annotators(self) -> Optional[bool]:
        return self._model.visible_for_annotators

    @visible_for_annotators.setter
    def visible_for_annotators(self, value: Optional[bool]) -> None:
        self._model.visible_for_annotators = value

    @property
    def dataset(self) -> Optional["Dataset"]:
        return self._dataset

    @dataset.setter
    def dataset(self, value: "Dataset") -> None:
        self._dataset = value
        self._model.dataset_id = value.id

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name}, title={self.title}, dimensions={self.visible_for_annotators})"
        )


class TermsMetadataProperty(MetadataPropertyBase):
    def __init__(
        self,
        name: str,
        options: Optional[List[str]] = None,
        title: Optional[str] = None,
        visible_for_annotators: Optional[bool] = True,
        client: Optional[Argilla] = None,
    ) -> None:
        """Create a metadata field with terms settings.

        Parameters:
            name (str): The name of the metadata field
            options (Optional[List[str]]): The list of options
            title (Optional[str]): The title of the metadata field
            visible_for_annotators (Optional[bool]): Whether the metadata field is visible for annotators
        Raises:
            MetadataError: If an error occurs while defining metadata settings
        """
        super().__init__(client=client)

        try:
            settings = TermsMetadataPropertySettings(values=options, type=MetadataPropertyType.terms)
        except ValueError as e:
            raise MetadataError(f"Error defining metadata settings for {name}") from e

        self._model = MetadataFieldModel(
            name=name,
            type=MetadataPropertyType.terms,
            title=title,
            settings=settings,
            visible_for_annotators=visible_for_annotators,
        )

    @property
    def options(self) -> Optional[List[str]]:
        return self._model.settings.values

    @options.setter
    def options(self, value: list[str]) -> None:
        self._model.settings.values = value

    @classmethod
    def from_model(cls, model: MetadataFieldModel) -> "TermsMetadataProperty":
        instance = TermsMetadataProperty(name=model.name)
        instance._model = model

        return instance


class FloatMetadataProperty(MetadataPropertyBase):
    def __init__(
        self,
        name: str,
        min: Optional[float] = None,
        max: Optional[float] = None,
        title: Optional[str] = None,
        client: Optional[Argilla] = None,
    ) -> None:
        """Create a metadata field with float settings.

        Parameters:
            name (str): The name of the metadata field
            min (Optional[float]): The minimum value
            max (Optional[float]): The maximum value
            title (Optional[str]): The title of the metadata field
            client (Optional[Argilla]): The client to use for API requests
        Raises:
            MetadataError: If an error occurs while defining metadata settings

        """

        super().__init__(client=client)

        try:
            settings = FloatMetadataPropertySettings(min=min, max=max, type=MetadataPropertyType.float)
        except ValueError as e:
            raise MetadataError(f"Error defining metadata settings for {name}") from e

        self._model = MetadataFieldModel(
            name=name,
            type=MetadataPropertyType.float,
            title=title,
            settings=settings,
        )

    @property
    def min(self) -> Optional[int]:
        return self._model.settings.min

    @min.setter
    def min(self, value: Optional[int]) -> None:
        self._model.settings.min = value

    @property
    def max(self) -> Optional[int]:
        return self._model.settings.max

    @max.setter
    def max(self, value: Optional[int]) -> None:
        self._model.settings.max = value

    @classmethod
    def from_model(cls, model: MetadataFieldModel) -> "FloatMetadataProperty":
        instance = FloatMetadataProperty(name=model.name)
        instance._model = model

        return instance


class IntegerMetadataProperty(MetadataPropertyBase):
    def __init__(
        self,
        name: str,
        min: Optional[int] = None,
        max: Optional[int] = None,
        title: Optional[str] = None,
        client: Optional[Argilla] = None,
    ) -> None:
        """Create a metadata field with integer settings.

        Parameters:
            name (str): The name of the metadata field
            min (Optional[int]): The minimum value
            max (Optional[int]): The maximum value
            title (Optional[str]): The title of the metadata field
        Raises:
            MetadataError: If an error occurs while defining metadata settings
        """
        super().__init__(client=client)

        try:
            settings = IntegerMetadataPropertySettings(min=min, max=max, type=MetadataPropertyType.integer)
        except ValueError as e:
            raise MetadataError(f"Error defining metadata settings for {name}") from e

        self._model = MetadataFieldModel(
            name=name,
            type=MetadataPropertyType.integer,
            title=title,
            settings=settings,
        )

    @property
    def min(self) -> Optional[int]:
        return self._model.settings.min

    @min.setter
    def min(self, value: Optional[int]) -> None:
        self._model.settings.min = value

    @property
    def max(self) -> Optional[int]:
        return self._model.settings.max

    @max.setter
    def max(self, value: Optional[int]) -> None:
        self._model.settings.max = value

    @classmethod
    def from_model(cls, model: MetadataFieldModel) -> "IntegerMetadataProperty":
        instance = IntegerMetadataProperty(name=model.name)
        instance._model = model

        return instance


MetadataType = Union[
    TermsMetadataProperty,
    FloatMetadataProperty,
    IntegerMetadataProperty,
]


class MetadataField:
    @classmethod
    def from_model(cls, model: MetadataFieldModel) -> MetadataType:
        switch = {
            MetadataPropertyType.terms: TermsMetadataProperty,
            MetadataPropertyType.float: FloatMetadataProperty,
            MetadataPropertyType.integer: IntegerMetadataProperty,
        }
        metadata_type = model.type
        try:
            return switch[metadata_type].from_model(model)
        except KeyError as e:
            raise MetadataError(f"Unknown metadata property type: {metadata_type}") from e

    @classmethod
    def from_dict(cls, data: dict) -> MetadataType:
        switch = {
            MetadataPropertyType.terms: TermsMetadataProperty,
            MetadataPropertyType.float: FloatMetadataProperty,
            MetadataPropertyType.integer: IntegerMetadataProperty,
        }
        metadata_type = data["type"]
        try:
            metadata_model = MetadataFieldModel(**data)
            return switch[metadata_type].from_model(metadata_model)
        except KeyError as e:
            raise MetadataError(f"Unknown metadata property type: {metadata_type}") from e
