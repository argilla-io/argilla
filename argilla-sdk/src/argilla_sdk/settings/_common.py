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

from typing import Any, Optional, Union, List, Dict

from argilla_sdk._models import FieldBaseModel, QuestionBaseModel
from argilla_sdk._resource import Resource

__all__ = ["SettingsPropertyBase"]


class SettingsPropertyBase(Resource):
    """Base class for dataset fields or questions in Settings class"""

    _model: Union[FieldBaseModel, QuestionBaseModel]

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

    @property
    def required(self) -> bool:
        return self._model.required

    @property
    def description(self) -> Optional[str]:
        return self._model.description

    @property
    def type(self) -> str:
        return self._model.settings.type

    def serialize(self) -> dict[str, Any]:
        serialized_model = super().serialize()
        serialized_model["type"] = self.type
        return serialized_model

    ##############################
    #  Private methods
    ##############################

    @staticmethod
    def _render_values_as_options(values: Union[List[str], List[int], Dict[str, str]]) -> List[Dict[str, str]]:
        """Render values as options for the question so that the model conforms to the API schema"""
        if isinstance(values, dict):
            return [{"text": value, "value": key} for key, value in values.items()]
        elif isinstance(values, list) and all(isinstance(value, str) for value in values):
            return [{"text": label, "value": label} for label in values]
        elif isinstance(values, list) and all(isinstance(value, int) for value in values):
            return [{"value": value} for value in values]
        else:
            raise ValueError("Invalid labels format. Please provide a list of strings or a list of dictionaries.")

    @staticmethod
    def _render_options_as_values(options: List[dict]) -> Dict[str, str]:
        """Render options as values for the question so that the model conforms to the API schema"""
        values = {}
        for option in options:
            if "text" in option:
                values[option["value"]] = option["text"]
            else:
                values[option["value"]] = option["value"]
        return values

    @staticmethod
    def _render_options_as_labels(options: List[Dict[str, str]]) -> List[str]:
        """Render values as labels for the question so that they can be returned as a list of strings"""
        return list(SettingsPropertyBase._render_options_as_values(options=options).keys())
