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

from typing import List

from argilla_server.models import VectorSettings


class VectorValidator:
    def __init__(self, value: List[float]):
        self._value = value

    def validate_for(self, vector_settings: VectorSettings):
        if len(self._value) != vector_settings.dimensions:
            raise ValueError(
                f"vector value for vector name={vector_settings.name} must have {vector_settings.dimensions} elements, "
                f"got {len(self._value)} elements"
            )
