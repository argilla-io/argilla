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

import json
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

from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes


class DatasetConfig(BaseModel):
    fields: List[AllowedFieldTypes]
    questions: List[Annotated[AllowedQuestionTypes, Field(..., discriminator="type")]]
    guidelines: Optional[str] = None

    def to_yaml(self) -> str:
        return dump(self.dict())

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "DatasetConfig":
        yaml_str = re.sub(r"(\n\s*|)id: !!python/object:uuid\.UUID\s+int: \d+", "", yaml_str)
        yaml_dict = load(yaml_str, Loader=SafeLoader)
        # Here for backwards compatibility
        for field in yaml_dict["fields"]:
            field.pop("id", None)
            field.pop("settings", None)
        for question in yaml_dict["questions"]:
            question.pop("id", None)
            question.pop("settings", None)
        return cls(**yaml_dict)


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
    def from_json(cls, json_str: str) -> "DeprecatedDatasetConfig":
        warnings.warn(
            "`DatasetConfig` can just be loaded from YAML, so make sure that you are"
            " loading a YAML file instead of a JSON file. `DatasetConfig` will be dumped"
            " as YAML from now on, instead of JSON.",
            DeprecationWarning,
        )
        parsed_json = json.loads(json_str)
        # Here for backwards compatibility
        for field in parsed_json["fields"]:
            # for 1.10.0, 1.9.0, and 1.8.0
            field.pop("id", None)
            field.pop("inserted_at", None)
            field.pop("updated_at", None)
            if "settings" not in field:
                continue
            field["type"] = field["settings"]["type"]
            if "use_markdown" in field["settings"]:
                field["use_markdown"] = field["settings"]["use_markdown"]
            # for 1.12.0 and 1.11.0
            field.pop("settings", None)
        for question in parsed_json["questions"]:
            # for 1.10.0, 1.9.0, and 1.8.0
            question.pop("id", None)
            question.pop("inserted_at", None)
            question.pop("updated_at", None)
            if "settings" not in question:
                continue
            question.update({"type": question["settings"]["type"]})
            if question["type"] in ["rating", "ranking"]:
                question["values"] = [option["value"] for option in question["settings"]["options"]]
            elif question["type"] in ["label_selection", "multi_label_selection"]:
                if all(option["value"] == option["text"] for option in question["settings"]["options"]):
                    question["labels"] = [option["value"] for option in question["settings"]["options"]]
                else:
                    question["labels"] = {option["value"]: option["text"] for option in question["settings"]["options"]}
                if "visible_labels" in question["settings"]:
                    question["visible_labels"] = question["settings"]["visible_labels"]
            # for 1.12.0 and 1.11.0
            question.pop("settings", None)
        return cls(**parsed_json)
