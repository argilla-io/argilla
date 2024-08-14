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
from abc import ABC
from typing import Optional, Union, TYPE_CHECKING

from argilla import Argilla
from argilla._api import FieldsAPI
from argilla._exceptions import ArgillaError
from argilla._models import FieldModel, TextFieldSettings
from argilla._models._settings._fields import ImageFieldSettings, FieldSettings
from argilla.settings._common import SettingsPropertyBase
from argilla.settings._metadata import MetadataField, MetadataType
from argilla.settings._vector import VectorField

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

if TYPE_CHECKING:
    from argilla.datasets import Dataset

__all__ = ["Field", "TextField", "ImageField", "AbstractField"]


class AbstractField(ABC, SettingsPropertyBase):
    """Abstract base class to work with Field resources"""

    _model: FieldModel
    _api: FieldsAPI
    _dataset: Optional["Dataset"]

    def __init__(
        self,
        name: str,
        settings: FieldSettings,
        title: Optional[str] = None,
        required: Optional[bool] = True,
        description: Optional[str] = None,
        _client: Optional[Argilla] = None,
    ):
        client = _client or Argilla._get_default()

        super().__init__(api=client.api.fields, client=client)

        self._dataset = None
        self._model = FieldModel(name=name, settings=settings, title=title, required=required, description=description)

    @classmethod
    def from_model(cls, model: FieldModel) -> "Self":
        instance = cls(name=model.name)  # noqa
        instance._model = model

        return instance

    @classmethod
    def from_dict(cls, data: dict) -> "Self":
        model = FieldModel(**data)
        return cls.from_model(model)

    @property
    def dataset(self) -> "Dataset":
        return self._dataset

    @dataset.setter
    def dataset(self, value: "Dataset") -> None:
        self._dataset = value
        self._model.dataset_id = self._dataset.id
        self._with_client(self._dataset._client)

    def _with_client(self, client: "Argilla") -> "Self":
        # TODO: Review and simplify. Maybe only one of them is required
        self._client = client
        self._api = self._client.api.fields

        return self


class TextField(AbstractField):
    """Text field for use in Argilla `Dataset` `Settings`"""

    def __init__(
        self,
        name: str,
        title: Optional[str] = None,
        use_markdown: Optional[bool] = False,
        required: Optional[bool] = True,
        description: Optional[str] = None,
        client: Optional[Argilla] = None,
    ) -> None:
        """Text field for use in Argilla `Dataset` `Settings`
        Parameters:
            name (str): The name of the field
            title (Optional[str], optional): The title of the field. Defaults to None.
            use_markdown (Optional[bool], optional): Whether to use markdown. Defaults to False.
            required (Optional[bool], optional): Whether the field is required. Defaults to True.
            description (Optional[str], optional): The description of the field. Defaults to None.

        """

        super().__init__(
            name=name,
            title=title,
            required=required or True,
            description=description,
            settings=TextFieldSettings(use_markdown=use_markdown),
            _client=client,
        )

    @property
    def use_markdown(self) -> Optional[bool]:
        return self._model.settings.use_markdown

    @use_markdown.setter
    def use_markdown(self, value: bool) -> None:
        self._model.settings.use_markdown = value


class ImageField(AbstractField):
    """Image field for use in Argilla `Dataset` `Settings`"""

    def __init__(
        self,
        name: str,
        title: Optional[str] = None,
        required: Optional[bool] = True,
        description: Optional[str] = None,
        _client: Optional[Argilla] = None,
    ) -> None:
        """
        Text field for use in Argilla `Dataset` `Settings`

        Parameters:
            name (str): The name of the field
            title (Optional[str], optional): The title of the field. Defaults to None.
            required (Optional[bool], optional): Whether the field is required. Defaults to True.
            description (Optional[str], optional): The description of the field. Defaults to None.
        """

        super().__init__(
            name=name,
            title=title,
            required=required,
            description=description,
            settings=ImageFieldSettings(),
            _client=_client,
        )


Field = Union[TextField, ImageField]


def _field_from_model(model: FieldModel) -> Field:
    if model.settings.type == "text":
        return TextField.from_model(model)
    elif model.settings.type == "image":
        return ImageField.from_model(model)
    else:
        raise ArgillaError(f"Unsupported field type: {model.settings.type}")


def _field_from_dict(data: dict) -> Union[Field, VectorField, MetadataType]:
    """Create a field instance from a field dictionary"""
    field_type = data["type"]

    if field_type == "text":
        return TextField.from_dict(data)
    elif field_type == "image":
        return ImageField.from_dict(data)
    elif field_type == "vector":
        return VectorField.from_dict(data)
    elif field_type == "metadata":
        return MetadataField.from_dict(data)
    else:
        raise ArgillaError(f"Unsupported field type: {field_type}")
