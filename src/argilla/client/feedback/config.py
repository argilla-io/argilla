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

from typing import List, Optional

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from pydantic import BaseModel, Field
from yaml import SafeLoader, dump, load

from argilla.client.feedback.typing import AllowedFieldTypes, AllowedQuestionTypes


class DatasetConfig(BaseModel):
    fields: List[AllowedFieldTypes]
    questions: List[Annotated[AllowedQuestionTypes, Field(..., discriminator="type")]]
    guidelines: Optional[str] = None

    def to_yaml(self):
        return dump(self.dict())

    @classmethod
    def from_yaml(cls, yaml):
        return cls(**load(yaml, Loader=SafeLoader))
