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

from typing import Optional, Union, TYPE_CHECKING

from argilla import Argilla
from argilla._api import FieldsAPI
from argilla._models import FieldModel, TextFieldSettings
from argilla.settings._common import SettingsPropertyBase
from argilla.settings._metadata import MetadataField, MetadataType
from argilla.settings._vector import VectorField

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

if TYPE_CHECKING:
    from argilla.datasets import Dataset

__all__ = ["TextField"]


class TextField(SettingsPropertyBase):
    """Text field for use in Argilla `Dataset` `Settings`"""

    _model: FieldModel
    _api: FieldsAPI

    _dataset: Optional["Dataset"]

    def __init__(
        self,
        name: str,
        title: Optional[str] = None,
        use_markdown: Optional[bool] = False,
        required: bool = True,
        description: Optional[str] = None,
        client: Optional[Argilla] = None,
    ) -> None:
        """Text field for use in Argilla `Dataset` `Settings`

        Parameters:
            name (str): The name of the field
            title (Optional[str]): The name of the field, as it will be displayed in the UI.
            use_markdown (Optional[bool]): Whether to render the markdown in the UI. When True, you will be able \
                to use all the Markdown features for text formatting, including LaTex formulas and embedding multimedia content and PDFs.
            required (bool): Whether the field is required. At least one field must be required.
            description (Optional[str]): The description of the field.
        """
        client = client or Argilla._get_default()

        super().__init__(api=client.api.fields, client=client)

        self._model = FieldModel(
            name=name,
            title=title,
            required=required,
            description=description,
            settings=TextFieldSettings(use_markdown=use_markdown),
        )

        self._dataset = None

    @classmethod
    def from_model(cls, model: FieldModel) -> "TextField":
        instance = cls(name=model.name)
        instance._model = model

        return instance

    @classmethod
    def from_dict(cls, data: dict) -> "TextField":
        model = FieldModel(**data)
        return cls.from_model(model=model)

    @property
    def use_markdown(self) -> Optional[bool]:
        return self._model.settings.use_markdown

    @use_markdown.setter
    def use_markdown(self, value: bool) -> None:
        self._model.settings.use_markdown = value

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


def field_from_dict(data: dict) -> Union[TextField, VectorField, MetadataType]:
    """Create a field instance from a field dictionary"""
    if data["type"] == "text":
        return TextField.from_dict(data)
    elif data["type"] == "vector":
        return VectorField.from_dict(data)
    elif data["type"] == "metadata":
        return MetadataField.from_dict(data)
    else:
        raise ValueError(f"Unsupported field type: {data['type']}")
