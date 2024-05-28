# Copyright 2024-present, Argilla, Inc.
# TODO: This license is not consistent with the license used in the project.
#       Delete the inconsistent license and above line and rerun pre-commit to insert a good license.
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

from enum import Enum

from pydantic import Field

from argilla_sdk._models._settings._questions._label_selection import LabelQuestionModel, LabelQuestionSettings


class OptionsOrder(str, Enum):
    natural = "natural"
    suggestion = "suggestion"


class MultiLabelQuestionSettings(LabelQuestionSettings):
    type: str = "multi_label_selection"
    options_order: OptionsOrder = Field(OptionsOrder.natural, description="The order of the labels in the UI.")


class MultiLabelQuestionModel(LabelQuestionModel):
    settings: MultiLabelQuestionSettings
