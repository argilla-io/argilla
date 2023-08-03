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

import re
import warnings
from typing import List, Optional

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from pydantic import BaseModel, Field

try:
    from yaml import SafeLoader, dump, load
except ImportError:
    raise ImportError(
        "Please make sure to install `PyYAML` in order to use `DatasetConfig`. To do"
        " so you can run `pip install pyyaml`."
    )

from argilla.client.feedback.types import AllowedFieldTypes, AllowedQuestionTypes


class DatasetConfig(BaseModel):
    fields: List[AllowedFieldTypes]
    questions: List[Annotated[AllowedQuestionTypes, Field(..., discriminator="type")]]
    guidelines: Optional[str] = None

    def to_yaml(self) -> str:
        return dump(self.dict(exclude={"fields": {"__all__": {"id"}}, "questions": {"__all__": {"id"}}}))

    @classmethod
    def from_yaml(cls, yaml: str) -> "DatasetConfig":
        yaml = re.sub(r"(\n\s*|)id: !!python/object:uuid\.UUID\s+int: \d+", "", yaml)
        return cls(**load(yaml, Loader=SafeLoader))


# TODO(alvarobartt): here for backwards compatibility, remove in 1.14.0
class DeprecatedDatasetConfig(BaseModel):
    fields: List[AllowedFieldTypes]
    questions: List[AllowedQuestionTypes]
    guidelines: Optional[str] = None

    def to_json(self) -> str:
        warnings.warn(
            "`DatasetConfig` can just be dumped to YAML, so make sure that you are"
            " dumping to a YAML file instead of a JSON file. `DatasetConfig` will come"
            " in YAML format from now on, instead of JSON format.",
            DeprecationWarning,
        )
        return self.json()

    @classmethod
    def from_json(cls, json: str) -> "DeprecatedDatasetConfig":
        warnings.warn(
            "`DatasetConfig` can just be loaded from YAML, so make sure that you are"
            " loading a YAML file instead of a JSON file. `DatasetConfig` will be dumped"
            " as YAML from now on, instead of JSON.",
            DeprecationWarning,
        )
        return cls.parse_raw(json)
