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

import dataclasses
from typing import List

from ._fields import Field
from ._questions import Question

__all__ = ["DatasetConfiguration"]


@dataclasses.dataclass
class DatasetConfiguration:
    guidelines: str
    allow_extra_metadata: bool = True

    fields: List[Field] = dataclasses.field(default_factory=list)
    questions: List[Question] = dataclasses.field(default_factory=list)

    def validate(self):
        for field in self.fields:
            field.validate()

        for question in self.questions:
            question.validate()

    def to_dict(self):
        return {
            "guidelines": self.guidelines,
            "allow_extra_metadata": self.allow_extra_metadata,
            "fields": [f.to_dict() for f in self.fields],
            "questions": [q.to_dict() for q in self.questions],
        }
