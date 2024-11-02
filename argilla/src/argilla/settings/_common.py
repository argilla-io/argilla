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

from typing import Any, Optional, Union

from argilla._models import FieldModel, QuestionBaseModel
from argilla._resource import Resource

__all__ = ["SettingsPropertyBase"]


class SettingsPropertyBase(Resource):
    """Base class for dataset fields or questions in Settings class"""

    _model: Union[FieldModel, QuestionBaseModel]

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name}, title={self.title}, description={self.description}, "
            f"type={self.type}, required={self.required}) \n"
        )

    @property
    def name(self) -> str:
        return self._model.name

    @property
    def title(self) -> Optional[str]:
        return self._model.title

    @title.setter
    def title(self, value: str):
        self._model.title = value

    @property
    def required(self) -> bool:
        return self._model.required

    @required.setter
    def required(self, value: bool):
        self._model.required = value

    @property
    def description(self) -> Optional[str]:
        return self._model.description

    @description.setter
    def description(self, value: str):
        self._model.description = value

    @property
    def type(self) -> str:
        return self._model.settings.type

    def validate(self):
        pass

    def serialize(self) -> dict[str, Any]:
        serialized_model = super().serialize()
        serialized_model["type"] = self.type
        return serialized_model
